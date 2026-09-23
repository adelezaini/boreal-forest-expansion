#!/usr/bin/env python3
"""Fill missing monthly LPJ-GUESS FPC and LAI cells by nearest neighbour.

The script reads the four configured monthly files, completes them on the
reference grid, writes new files ending in ``_fullgrid``, and records the donor
used for every reconstructed cell. The original input files are not changed.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
# cKDTree:
# - determines the donor cell once;
# - copies all 12 months and PFT columns from that donor;
# - guarantees FPC and LAI use the same donor mapping;
# - records donor coordinates and distances in the audit file.


# =============================================================================
# Settings: normally these are the only lines you may want to change
# =============================================================================

LPJ_DIR = Path.home() / "BOREAL-FOREST-EXPANSION/data/edit-surfdata/LPJ-GUESS"

# "fill-only" keeps every original value and fills only missing cells.
# "shared-common" reconstructs every non-common cell in both periods.
MODE = "fill-only"

MAX_DISTANCE_KM = 150.0

REFERENCE_FILE = LPJ_DIR / "gridlist45N_tundraboreal.txt"
INPUT_FILES = {
    "historical_fpc": LPJ_DIR / "mfpc_pft_avg_1971_2000_monthly_mean.out",
    "historical_lai": LPJ_DIR / "mlai_pft_avg_1971_2000_monthly_mean.out",
    "future_fpc": LPJ_DIR / "mfpc_pft_avg_2070_2100_monthly_mean.out",
    "future_lai": LPJ_DIR / "mlai_pft_avg_2070_2100_monthly_mean.out",
}


# =============================================================================
# Read and check the input files
# =============================================================================

KEYS = ["Lon", "Lat", "Month"]
EARTH_RADIUS_KM = 6371.0088


def read_reference(path):
    """Read the two-column longitude/latitude reference grid.

    Coordinates are converted to numbers and rounded to eight decimal places
    so that tiny text-format differences do not prevent coordinate matching.
    The returned table contains one unique row per reference-grid cell.
    """
    reference = pd.read_csv(path, sep=r"\s+", header=None, names=["Lon", "Lat"])
    reference = reference.apply(pd.to_numeric, errors="raise").round(8)
    if reference.duplicated(["Lon", "Lat"]).any():
        raise ValueError(f"{path}: duplicate coordinates")
    return reference.reset_index(drop=True)


def read_monthly(path):
    """Read and validate one monthly FPC or LAI file.

    Repeated header lines are discarded, all remaining fields are converted to
    numbers, and coordinates are rounded to eight decimal places. The function
    also checks that every coordinate has exactly one row for each month 1-12.
    """
    data = pd.read_csv(path, sep=r"\s+", dtype=str, low_memory=False)
    if not set(KEYS).issubset(data.columns):
        raise ValueError(f"{path}: expected the columns {KEYS}")

    # Remove repeated header rows, then convert the table to numbers.
    numeric_keys = data[KEYS].apply(pd.to_numeric, errors="coerce")
    data = data.loc[numeric_keys.notna().all(axis=1)].copy()
    data = data.apply(pd.to_numeric, errors="raise")
    data[["Lon", "Lat"]] = data[["Lon", "Lat"]].round(8)
    data["Month"] = data["Month"].astype(int)

    if data.duplicated(KEYS).any():
        raise ValueError(f"{path}: duplicate Lon/Lat/Month rows")
    if set(data["Month"].unique()) != set(range(1, 13)):
        raise ValueError(f"{path}: expected months 1-12")
    if not data.groupby(["Lon", "Lat"])["Month"].nunique().eq(12).all():
        raise ValueError(f"{path}: some cells do not contain all 12 months")
    return data


def cell_index(data):
    """Return the unique Lon/Lat cells in a table as a sorted index."""
    cells = data[["Lon", "Lat"]].drop_duplicates().sort_values(["Lon", "Lat"])
    return pd.MultiIndex.from_frame(cells, names=["Lon", "Lat"])


# =============================================================================
# Find the nearest donor cell on the sphere
# =============================================================================

def to_xyz(coordinates):
    """Convert Lon/Lat degrees to 3-D points on a unit sphere.

    Searching in spherical Cartesian coordinates avoids problems near the
    dateline and makes the nearest-neighbour search geographically meaningful.
    """
    lon = np.deg2rad(coordinates[:, 0])
    lat = np.deg2rad(coordinates[:, 1])
    return np.column_stack([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])


def nearest_mapping(target_cells, donor_cells, period):
    """Match every target cell to its nearest available donor cell.

    A k-d tree performs the search on the unit sphere. The returned table has
    one row per target, including target coordinates, donor coordinates, the
    great-circle distance in kilometres, period, and interpolation mode.
    """
    targets = target_cells.to_frame(index=False).to_numpy(float)
    donors = donor_cells.to_frame(index=False).to_numpy(float)
    if not len(targets):
        return pd.DataFrame(columns=[
            "target_lon", "target_lat", "donor_lon", "donor_lat",
            "distance_km", "period", "mode",
        ])

    distance, donor_position = cKDTree(to_xyz(donors)).query(to_xyz(targets))
    angle = 2 * np.arcsin(np.clip(distance / 2, 0, 1))
    return pd.DataFrame({
        "target_lon": targets[:, 0],
        "target_lat": targets[:, 1],
        "donor_lon": donors[donor_position, 0],
        "donor_lat": donors[donor_position, 1],
        "distance_km": EARTH_RADIUS_KM * angle,
        "period": period,
        "mode": MODE,
    })


def reconstruct_cells(data, mapping):
    """Copy each donor's complete 12-month cycle to its target coordinate.

    Only Lon and Lat are replaced; Month and every FPC/LAI value are copied
    unchanged. Existing target rows are removed first, which matters in
    ``shared-common`` mode where some originally present cells are rebuilt.
    """
    value_columns = [column for column in data.columns if column not in KEYS]
    target_index = pd.MultiIndex.from_arrays(
        [mapping["target_lon"], mapping["target_lat"]], names=["Lon", "Lat"]
    )
    data_cells = pd.MultiIndex.from_frame(data[["Lon", "Lat"]])
    output = data.loc[~data_cells.isin(target_index)].copy()
    indexed = data.set_index(["Lon", "Lat", "Month"]).sort_index()

    new_cells = []
    for row in mapping.itertuples(index=False):
        donor = indexed.loc[(row.donor_lon, row.donor_lat), value_columns].reset_index()
        donor.insert(0, "Lat", row.target_lat)
        donor.insert(0, "Lon", row.target_lon)
        new_cells.append(donor[[*KEYS, *value_columns]])

    return pd.concat([output, *new_cells], ignore_index=True)


# =============================================================================
# Order, validate and write the completed datasets
# =============================================================================

def order_on_reference(data, reference):
    """Order output cells like the reference grid and months from 1 to 12.

    The merge also detects any output coordinate that does not belong to the
    configured reference grid.
    """
    order = reference.copy()
    order["_order"] = np.arange(len(order))
    data = data.merge(order, on=["Lon", "Lat"], how="left", validate="many_to_one")
    if data["_order"].isna().any():
        raise ValueError("Output contains coordinates outside the reference grid")
    return data.sort_values(["_order", "Month"]).drop(columns="_order").reset_index(drop=True)


def check_complete(data, reference_index):
    """Verify that output contains every reference cell for all 12 months.

    The checks reject duplicate Lon/Lat/Month rows, absent grid cells, missing
    months, and any row count inconsistent with a complete monthly grid.
    """
    if len(data) != len(reference_index) * 12 or data.duplicated(KEYS).any():
        raise ValueError("Output is not one row per reference cell and month")
    if len(reference_index.difference(cell_index(data))):
        raise ValueError("Output is still missing reference-grid cells")
    if not data.groupby(["Lon", "Lat"])["Month"].nunique().eq(12).all():
        raise ValueError("Output contains incomplete monthly cycles")


def output_path(input_path):
    """Return an input path with ``_fullgrid`` inserted before its suffix."""
    return input_path.with_name(f"{input_path.stem}_fullgrid{input_path.suffix}")


def write_readme():
    """Write a short provenance note beside the generated output files."""
    if MODE == "fill-only":
        donor_text = (
            "Historical and future files were treated separately. Within each\n"
            "period, the same donor mapping was used for FPC and LAI."
        )
    else:
        donor_text = (
            "The same donor mapping was used for historical and future FPC and\n"
            "LAI."
        )

    readme = f"""# Monthly LPJ-GUESS full-grid files

Files ending in `_fullgrid` are **processed data, not original LPJ-GUESS
output**. They were created because the original monthly FPC and LAI files did
not contain every longitude-latitude combination in
`gridlist45N_tundraboreal.txt`.

The missing cells were reconstructed with spherical nearest-neighbour
interpolation. {donor_text}

`nearest_neighbour_donor_audit_fullgrid.csv` records every reconstructed
cell, its donor coordinates and the donor distance.
"""
    (LPJ_DIR / "README_fullgrid_interpolation.md").write_text(readme, encoding="utf-8")


# =============================================================================
# Main workflow
# =============================================================================

def main():
    """Run the complete interpolation, validation, and output workflow.

    In ``fill-only`` mode, historical and future missing cells are found and
    filled separately. In ``shared-common`` mode, one donor mapping based on
    cells common to all four inputs is applied to all four datasets.
    """
    if MODE not in {"fill-only", "shared-common"}:
        raise ValueError("MODE must be 'fill-only' or 'shared-common'")

    reference = read_reference(REFERENCE_FILE)
    reference_index = cell_index(reference)
    data = {name: read_monthly(path) for name, path in INPUT_FILES.items()}
    supports = {name: cell_index(frame) for name, frame in data.items()}

    for period in ["historical", "future"]:
        if not supports[f"{period}_fpc"].equals(supports[f"{period}_lai"]):
            raise ValueError(f"{period}: FPC and LAI grids differ")
    for name, support in supports.items():
        if len(support.difference(reference_index)):
            raise ValueError(f"{name}: cells found outside the reference grid")

    mappings = []
    completed = {}

    if MODE == "fill-only":
        for period in ["historical", "future"]:
            donors = supports[f"{period}_fpc"]
            targets = reference_index.difference(donors)
            mapping = nearest_mapping(targets, donors, period)
            mappings.append(mapping)
            for variable in ["fpc", "lai"]:
                name = f"{period}_{variable}"
                completed[name] = reconstruct_cells(data[name], mapping)
    else:
        common = reference_index
        for support in supports.values():
            common = common.intersection(support)
        mapping = nearest_mapping(reference_index.difference(common), common, "both")
        mappings.append(mapping)
        completed = {name: reconstruct_cells(frame, mapping) for name, frame in data.items()}

    audit = pd.concat(mappings, ignore_index=True)
    if len(audit) and audit["distance_km"].max() > MAX_DISTANCE_KM:
        raise ValueError(
            f"Maximum donor distance is {audit['distance_km'].max():.2f} km, "
            f"above the {MAX_DISTANCE_KM:.2f} km limit"
        )

    output_paths = {name: output_path(path) for name, path in INPUT_FILES.items()}
    for name, frame in completed.items():
        frame = order_on_reference(frame, reference)
        check_complete(frame, reference_index)
        frame.to_csv(output_paths[name], sep="\t", index=False, float_format="%.6f")

    audit_path = LPJ_DIR / "nearest_neighbour_donor_audit_fullgrid.csv"
    audit.to_csv(audit_path, index=False, float_format="%.6f")
    write_readme()

    print(f"Mode: {MODE}")
    print(f"Reference grid: {len(reference_index):,} cells")
    print("Original grids: " + ", ".join(f"{name}={len(index):,}" for name, index in supports.items()))
    if len(audit):
        print(f"Donor distance: median={audit.distance_km.median():.2f} km, max={audit.distance_km.max():.2f} km")
    print("Created:")
    for path in [*output_paths.values(), audit_path, LPJ_DIR / "README_fullgrid_interpolation.md"]:
        print(f"  {path}")


if __name__ == "__main__":
    main()
