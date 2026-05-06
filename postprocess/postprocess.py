"""
Executable postprocessing workflow.

Run after select_concat_cam_raw_output.sh.

Output folder:
    /cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/postprocessed-diagnostics

Output naming:
    [casealias]_[variableclass]_[startyr]_[endyr].nc

Example:
    CTRL_BVOC_2000_2009.nc
    LCC-PD_CH4_2000_2009.nc
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import xarray as xr

from boreal_forest_expansion.postprocess.transform import (
    open_selected_dataset,
    transform_dataset,
    annual_mean,
    climatology,
    select_present,
)
from boreal_forest_expansion.postprocess.ghan_decomposition import add_ghan_decomposition
from boreal_forest_expansion.postprocess.chemistry_postprocess import (
    make_monthly_diagnostics,
    make_annual_diagnostics,
    make_climatology,
    make_map_diagnostics,
    paired_comparison,
)
from boreal_forest_expansion.postprocess.variable_catalog import (
    VARIABLE_CLASSES,
    catalog_variable_union,
)

# =============================================================================
# User configuration
# =============================================================================

SELECTED_OUTPUT_DIR = Path(
    "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/selected-model-output"
)

POSTPROCESSED_DIR = Path(
    "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/postprocessed-diagnostics"
)

STREAM = "h0"
START_YEAR = 2000
END_YEAR = 2009
START_YM = f"{START_YEAR}-01"
END_YM = f"{END_YEAR}-12"

CLIM_START_YEAR = 2001
CLIM_END_YEAR = 2009

FIX_TIMESTAMP = "DatetimeNoLeap"
CHUNKS = {"time": 12}

WRITE_MAPS = True

OUTPUT_VARIABLE_CLASSES = [
    "METEOROLOGY",
    "CLOUDPROP",
    "SOA"
]


@dataclass(frozen=True)
class CaseConfig:
    alias: str
    casename: str
    start_year: int = START_YEAR
    end_year: int = END_YEAR
    stream: str = STREAM

    @property
    def selected_file(self) -> Path:
        start_ym = f"{self.start_year}-01"
        end_ym = f"{self.end_year}-12"
        fname = f"{self.casename}.cam.{self.stream}.{start_ym}_{end_ym}.nc"
        return SELECTED_OUTPUT_DIR / fname


CASES: list[CaseConfig] = [
    CaseConfig(
        alias="CTRL",
        casename="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429",
    ),
    CaseConfig(
        alias="LCC-PD",
        casename="NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20260502",
    ),
    CaseConfig(
        alias="LCC-PD-fBVOC",
        casename="NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20260503",
    ),
    CaseConfig(
        alias="LCC-FUT",
        casename="NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20260502",
    ),
    CaseConfig(
        alias="LCC-FUT-fBVOC",
        casename="NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20260503",
    ),
]

# Optional comparisons. These write files with comparison aliases.
COMPARISONS: list[tuple[str, str, str]] = [
    ("LCC-PD", "CTRL", "LCC-PD_minus_CTRL"),
    ("LCC-PD-fBVOC", "LCC-PD", "LCC-PD-fBVOC_minus_LCC-PD"),
    ("LCC-FUT", "LCC-PD", "LCC-FUT_minus_LCC-PD"),
    ("LCC-FUT-fBVOC", "LCC-FUT", "LCC-FUT-fBVOC_minus_LCC-FUT"),
]

# =============================================================================
# Output helpers
# =============================================================================

def output_path(case_alias: str, variable_class: str, start_year: int, end_year: int) -> Path:
    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return POSTPROCESSED_DIR / f"{case_alias}_{variable_class}_{start_year}_{end_year}.nc"


def write_if_nonempty(ds: xr.Dataset, path: Path) -> None:
    if len(ds.data_vars) == 0:
        print(f"Skipping empty output: {path.name}")
        return
    ds.to_netcdf(path)
    print(f"Wrote {path}")


def select_class(ds: xr.Dataset, variable_class: str) -> xr.Dataset:
    variables = VARIABLE_CLASSES[variable_class]
    return select_present(ds, variables, warn=False)


# =============================================================================
# Workflow
# =============================================================================

def open_case(case: CaseConfig) -> xr.Dataset:
    print(f"\nOpening {case.alias}: {case.selected_file}")
    return open_selected_dataset(case.selected_file, fix_timestamp=FIX_TIMESTAMP, chunks=CHUNKS)


def build_monthly_postprocessed_dataset(ds: xr.Dataset) -> xr.Dataset:
    """
    Build one coherent monthly postprocessed dataset from all modules.

    This is the smooth workflow:
    1. transform general variables, preserving native fields
    2. add Ghan radiative diagnostics when possible
    3. add compact chemistry/BVOC/CH4/O3 scalar diagnostics
    4. add map diagnostics when requested
    """
    transformed = transform_dataset(ds, add_display_units=True)
    radiative = add_ghan_decomposition(transformed, strict=False)

    catalog_vars = catalog_variable_union()
    radiative_selected = select_present(radiative, catalog_vars, warn=False)

    chemistry = make_monthly_diagnostics(ds)

    pieces = [radiative_selected, chemistry]

    if WRITE_MAPS:
        maps = make_map_diagnostics(ds)
        pieces.append(maps)

    return xr.merge(pieces, compat="override", join="outer")


def save_case_outputs(case: CaseConfig, monthly_all: xr.Dataset) -> xr.Dataset:
    annual_all = annual_mean(monthly_all)
    clim_all = climatology(
        annual_all,
        start_year=CLIM_START_YEAR,
        end_year=CLIM_END_YEAR,
    )

    for variable_class in OUTPUT_VARIABLE_CLASSES:
        print(f"Preparing {case.alias}_{variable_class}...", flush=True)
        out = select_class(clim_all, variable_class)
        write_if_nonempty(
            out,
            output_path(case.alias, variable_class, CLIM_START_YEAR, CLIM_END_YEAR),
        )

    print_sanity_checks(case, clim_all)
    return clim_all


def print_sanity_checks(case: CaseConfig, clim: xr.Dataset) -> None:
    print(f"\nSanity checks for {case.alias}")
    print("-" * 60)

    if "CH4_lifetime_OH_yr" in clim:
        tau = float(clim["CH4_lifetime_OH_yr"].values)
        print(f"CH4 lifetime wrt OH: {tau:.2f} yr")
        if tau < 5 or tau > 20:
            print("WARNING: CH4 lifetime outside broad expected range. Check CH4/OH/pressure units.")

    for var in ["MEG_ISOP_Tg_yr", "MEG_MTERP_Tg_yr", "CH4_OH_loss_Tg_yr", "OH_trop_massmean"]:
        if var in clim:
            val = float(clim[var].values)
            units = clim[var].attrs.get("units", "")
            print(f"{var}: {val:.4g} {units}")


def process_case(case: CaseConfig) -> xr.Dataset:
    ds = open_case(case)
    monthly_all = build_monthly_postprocessed_dataset(ds)
    return save_case_outputs(case, monthly_all)


def save_comparison_outputs(climatologies: dict[str, xr.Dataset], cases_by_alias: dict[str, CaseConfig]) -> None:
    for pert_alias, ctrl_alias, out_alias in COMPARISONS:
        if pert_alias not in climatologies or ctrl_alias not in climatologies:
            print(f"Skipping comparison {out_alias}: missing one or both cases")
            continue

        comp = paired_comparison(climatologies[pert_alias], climatologies[ctrl_alias])
        case = cases_by_alias[pert_alias]

        for variable_class in OUTPUT_VARIABLE_CLASSES:
            variables = VARIABLE_CLASSES[variable_class]
            selected = [var for var in comp.data_vars if any(var.startswith(base) for base in variables)]
            out = comp[selected] if selected else xr.Dataset(coords=comp.coords)
            write_if_nonempty(
                out,
                output_path(out_alias, variable_class, CLIM_START_YEAR, CLIM_END_YEAR),
            )

# =============================================================================
# CLI
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess selected CAM output into variable classes.")
    parser.add_argument("--case-alias", default=None, help="Run only one case by alias, e.g. CTRL or LCC-PD.")
    parser.add_argument("--start-year", type=int, default=None, help="Override start year.")
    parser.add_argument("--end-year", type=int, default=None, help="Override end year.")
    return parser.parse_args()


def cases_from_args(args: argparse.Namespace) -> list[CaseConfig]:
    cases = CASES

    if args.case_alias is not None:
        cases = [case for case in cases if case.alias == args.case_alias]
        if not cases:
            raise ValueError(f"No case found with alias {args.case_alias}")

    if args.start_year is not None or args.end_year is not None:
        start_year = args.start_year if args.start_year is not None else START_YEAR
        end_year = args.end_year if args.end_year is not None else END_YEAR
        cases = [
            CaseConfig(alias=case.alias, casename=case.casename, start_year=start_year, end_year=end_year, stream=case.stream)
            for case in cases
        ]

    return cases


def main() -> None:
    args = parse_args()
    cases = cases_from_args(args)

    POSTPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    climatologies: dict[str, xr.Dataset] = {}
    cases_by_alias = {case.alias: case for case in cases}

    for case in cases:
        climatologies[case.alias] = process_case(case)

    if args.case_alias is None:
        save_comparison_outputs(climatologies, cases_by_alias)


if __name__ == "__main__":
    main()