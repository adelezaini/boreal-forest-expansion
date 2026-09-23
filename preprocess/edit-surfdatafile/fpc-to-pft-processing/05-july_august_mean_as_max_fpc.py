#!/usr/bin/env python3
"""Create July-August mean FPC files in the annual FPC-file structure."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("~/BOREAL-FOREST-EXPANSION/data/edit-surfdata/LPJ-GUESS").expanduser()
OUTPUT_DIR = DATA_DIR #/ "FPC-July-August-mean"
PEAT_FRACTIONS = DATA_DIR / "lpj_global_gridlist_with_peatfrac.txt"

FILES = {
    "historical": {
        "monthly": DATA_DIR / "mfpc_pft_avg_1971_2000_monthly_mean_fullgrid.out",
        "template": DATA_DIR / "fpc1971to2000.txt",
        "output": OUTPUT_DIR / "fpc1971to2000_max.txt",
    },
    "future": {
        "monthly": DATA_DIR / "mfpc_pft_avg_2070_2100_monthly_mean_fullgrid.out",
        "template": DATA_DIR / "GFDL-ESM4_SSP585_fpc2071to2100.txt",
        "output": OUTPUT_DIR / "GFDL-ESM4_SSP585_fpc2071to2100_max.txt",
    },
}

NATURAL_PFTS = [
    "BNE", "BINE", "BNS", "TeNE", "TeBE", "IBS", "TeBS", "C3G",
    "HSE", "HSS", "LSE", "LSS", "GRT", "EPDS", "SPDS", "CLM",
]
PEATLAND_PFTS = ["pLSE", "pLSS", "pCLM", "WetGRS", "pmoss", "C3G_wet", "C4G_wet"]
PFTS = NATURAL_PFTS + PEATLAND_PFTS


def read_table(path):
    """Read a whitespace table, remove repeated headers and convert it to numbers."""
    if not path.exists():
        raise FileNotFoundError(path)

    table = pd.read_csv(path, sep=r"\s+", dtype=str, low_memory=False)
    if not {"Lon", "Lat"}.issubset(table.columns):
        raise ValueError(f"{path}: missing Lon or Lat")

    repeated_header = table["Lon"].eq("Lon") | table["Lat"].eq("Lat")
    table = table.loc[~repeated_header].copy()

    for column in table.columns:
        table[column] = pd.to_numeric(table[column], errors="raise")

    return table


def july_august_mean(monthly, path):
    """Average July and August for every grid cell and PFT."""
    required = {"Lon", "Lat", "Month", *PFTS}
    missing = required.difference(monthly.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")

    if monthly.duplicated(["Lon", "Lat", "Month"]).any():
        raise ValueError(f"{path}: duplicate Lon/Lat/Month rows")

    selected = monthly.loc[monthly["Month"].isin([7, 8]), ["Lon", "Lat", "Month", *PFTS]]
    month_count = selected.groupby(["Lon", "Lat"])["Month"].nunique()
    if month_count.ne(2).any():
        raise ValueError(f"{path}: some grid cells do not contain both July and August")

    if selected[PFTS].isna().any().any():
        raise ValueError(f"{path}: missing July or August PFT values")

    return selected.groupby(["Lon", "Lat"], as_index=False)[PFTS].mean()


def add_summary_columns(mean_fpc, fractions, path):
    """Calculate Natural_sum, Peatland_sum and land-cover-weighted Total."""
    needed = {"Lon", "Lat", "NATURAL", "PEATLAND"}
    missing = needed.difference(fractions.columns)
    if missing:
        raise ValueError(f"{PEAT_FRACTIONS}: missing columns {sorted(missing)}")

    if fractions.duplicated(["Lon", "Lat"]).any():
        raise ValueError(f"{PEAT_FRACTIONS}: duplicate Lon/Lat rows")

    result = mean_fpc.merge(
        fractions[["Lon", "Lat", "NATURAL", "PEATLAND"]],
        on=["Lon", "Lat"], how="left", validate="one_to_one",
    )
    if result[["NATURAL", "PEATLAND"]].isna().any().any():
        raise ValueError(f"{path}: some grid cells are absent from {PEAT_FRACTIONS.name}")

    result["Natural_sum"] = result[NATURAL_PFTS].sum(axis=1)
    result["Peatland_sum"] = result[PEATLAND_PFTS].sum(axis=1)
    result["Total"] = (
        result["Natural_sum"] * result["NATURAL"]
        + result["Peatland_sum"] * result["PEATLAND"]
    )
    return result.drop(columns=["NATURAL", "PEATLAND"])


def match_template(result, template, template_path):
    """Use the template's columns and coordinate row order."""
    if template.duplicated(["Lon", "Lat"]).any():
        raise ValueError(f"{template_path}: duplicate Lon/Lat rows")

    missing_columns = set(template.columns).difference(result.columns)
    if missing_columns:
        raise ValueError(f"{template_path}: unsupported columns {sorted(missing_columns)}")

    ordered = template[["Lon", "Lat"]].merge(
        result, on=["Lon", "Lat"], how="left", validate="one_to_one",
    )
    extra_cells = pd.MultiIndex.from_frame(result[["Lon", "Lat"]]).difference(
        pd.MultiIndex.from_frame(template[["Lon", "Lat"]])
    )
    if ordered.isna().any().any() or len(extra_cells):
        raise ValueError(
            f"Grid mismatch with {template_path.name}: "
            f"missing or extra cells are present"
        )

    return ordered[template.columns]


def write_and_check(result, output_path):
    """Write the result and verify its columns and numeric values."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, sep="\t", index=False, float_format="%.6f")

    written = read_table(output_path)

    if list(written.columns) != list(result.columns):
        raise AssertionError(f"{output_path}: output columns changed while writing")

    max_error = np.abs(written.to_numpy() - result.to_numpy()).max()
    if max_error > 5.1e-7:
        raise AssertionError(
            f"{output_path}: output values changed while writing "
            f"(maximum difference: {max_error:g})"
        )

    print(f"Written: {output_path}")


def main():
    fractions = read_table(PEAT_FRACTIONS)

    for period, paths in FILES.items():
        monthly = read_table(paths["monthly"])
        template = read_table(paths["template"])
        result = july_august_mean(monthly, paths["monthly"])
        result = add_summary_columns(result, fractions, paths["monthly"])
        result = match_template(result, template, paths["template"])
        write_and_check(result, paths["output"])
        print(f"  {period}: {len(result):,} grid cells")


if __name__ == "__main__":
    main()
