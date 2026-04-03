#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Create a modified surfdata file from LPJ-GUESS future and historical PFT data.

This is a cleaned version of the original notebook-derived script, keeping only the
steps needed to generate the new file, plus defensive checks/fixes so the output is
less likely to contain silent errors.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import xarray as xr

sys.path.append("..")
from dataset_manipulation import convert180_360, convert360_180, convert_lsmcoord  # noqa: E402
from surfdatamaplib import surfdatamap_modification  # noqa: E402
from lpjguess import DataArray_from_LPJGUESS, PFT_convert_LPJGUESS_to_CLM  # noqa: E402


# -----------------------------
# Paths / filenames
# -----------------------------
FN_IN = "surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304"
SURFDATA_DIR = Path("../../data/surfdatamap")
LPJ_DIR = Path("../../data/LPJ-GUESS/FPC")
FOLDER_OUT = Path("/Users/adelezaini/Desktop/master-thesis/processed-data/input")
REALISTIC_DIR = FOLDER_OUT / "REALISTIC"
IDEALIZED_DIR = FOLDER_OUT / "IDEALIZED"

SURFDATA_PATH = SURFDATA_DIR / f"{FN_IN}.nc"
LPJ_FUTURE_PATH = LPJ_DIR / "GFDL-ESM4_SSP585_fpc2071to2100.txt"
LPJ_HIST_PATH = LPJ_DIR / "fpc1971to2000.txt"
OUTPUT_PATH = REALISTIC_DIR / f"{FN_IN}_GFDL.nc"


# -----------------------------
# Utility functions
# -----------------------------
def require_path(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")



def require_var(ds: xr.Dataset, var_name: str, description: str | None = None) -> xr.DataArray:
    if var_name not in ds:
        desc = description or ds.encoding.get("source", "dataset")
        raise KeyError(f"Variable '{var_name}' not found in {desc}")
    return ds[var_name]



def check_dims_match(reference: xr.DataArray, other: xr.DataArray, label: str) -> None:
    if tuple(reference.dims) != tuple(other.dims):
        raise ValueError(
            f"Dimension mismatch for {label}: expected {reference.dims}, got {other.dims}"
        )
    for dim in reference.dims:
        if reference.sizes[dim] != other.sizes[dim]:
            raise ValueError(
                f"Size mismatch for {label} along '{dim}': "
                f"expected {reference.sizes[dim]}, got {other.sizes[dim]}"
            )



def sanitize_percentages(
    da: xr.DataArray,
    *,
    dim: str = "natpft",
    clip_min: float = 0.0,
    clip_max: float = 100.0,
    tol: float = 1e-8,
    label: str = "data",
) -> xr.DataArray:
    """Clip invalid values and renormalize to 100 where the total is positive.

    Keeps NaNs outside valid land cells. Raises if non-finite values remain in valid cells.
    """
    da = da.astype(np.float64)

    # Replace inf with nan, then clip physical range.
    da = da.where(np.isfinite(da))
    da = da.clip(min=clip_min, max=clip_max)

    total = da.sum(dim=dim, skipna=True)
    positive_total = total > tol

    # Renormalize only where there is vegetation information.
    da = xr.where(positive_total, da / total * 100.0, da)

    # Final clipping for tiny numeric overshoots/undershoots.
    da = da.clip(min=clip_min, max=clip_max)

    total_after = da.sum(dim=dim, skipna=True)
    bad_total = positive_total & (~np.isfinite(total_after) | (np.abs(total_after - 100.0) > 1e-4))
    if bool(bad_total.any()):
        count = int(bad_total.sum().item())
        raise ValueError(f"{label}: renormalization failed in {count} grid cells")

    bad_values = positive_total.broadcast_like(da) & ~np.isfinite(da)
    if bool(bad_values.any()):
        count = int(bad_values.sum().item())
        raise ValueError(f"{label}: found {count} non-finite values in valid cells")

    return da



def assert_subset_natpfts(da: xr.DataArray, natpfts: list[int], label: str) -> None:
    available = set(int(v) for v in da["natpft"].values.tolist())
    missing = [p for p in natpfts if p not in available]
    if missing:
        raise ValueError(f"{label}: missing natpft indices {missing}")



def run_regrid(src_nc: Path, target_nc: Path, out_dir: Path, out_name: str, method: str) -> Path:
    out_path = out_dir / out_name
    cmd = f'''eval "$(conda shell.bash hook)"
conda activate xesmf_env
python3 xe_regrid.py {src_nc.name} {target_nc.name} {out_dir}/ {out_name} {method}
conda activate base'''

    subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        check=True,
        cwd=out_dir,
    )
    if not out_path.exists():
        raise FileNotFoundError(f"Expected regridded file was not created: {out_path}")
    return out_path


# -----------------------------
# Main workflow
# -----------------------------
def main() -> None:
    REALISTIC_DIR.mkdir(parents=True, exist_ok=True)

    require_path(SURFDATA_PATH, "input surfdata file")
    require_path(LPJ_FUTURE_PATH, "future LPJ-GUESS file")
    require_path(LPJ_HIST_PATH, "historical LPJ-GUESS file")
    require_path(IDEALIZED_DIR / "pfts_CLM.nc", "CLM PFT file")
    require_path(IDEALIZED_DIR / "lndfrac_CLM.nc", "CLM land fraction file")

    dset_in = xr.open_dataset(SURFDATA_PATH)
    if "PCT_NAT_PFT" not in dset_in:
        raise KeyError(f"Variable 'PCT_NAT_PFT' not found in {SURFDATA_PATH}")

    pfts_clm_ds = xr.open_dataset(IDEALIZED_DIR / "pfts_CLM.nc")
    pfts_CLM = require_var(pfts_clm_ds, "PCT_NAT_PFT", "pfts_CLM.nc")

    lnd_frac_ds = xr.open_dataset(IDEALIZED_DIR / "lndfrac_CLM.nc")
    lnd_frac = require_var(lnd_frac_ds, "LANDFRAC_PFT", "lndfrac_CLM.nc")
    lnd_frac = lnd_frac.where(lnd_frac <= 1.0, 1.0)

    # Load LPJ-GUESS future distribution and keep natural PFTs only.
    pfts_GFDL = DataArray_from_LPJGUESS(
        str(LPJ_FUTURE_PATH),
        name="FPC_PFT",
        colnames=False,
        da_attrs=pfts_CLM,
        main_attrs={"long_name": "foliage projective cover (fraction of gridcell)"},
    ).isel(natpft=slice(0, 16))

    # Temporary files for regridding.
    pfts_gfdl_tmp = REALISTIC_DIR / "pfts_GFDL.nc"
    pfts_clm_tmp = REALISTIC_DIR / "pfts_CLM_real.nc"
    pfts_GFDL.load().to_netcdf(pfts_gfdl_tmp)
    pfts_CLM.load().to_netcdf(pfts_clm_tmp)

    pfts_gfdl_regridded = run_regrid(
        pfts_gfdl_tmp,
        pfts_clm_tmp,
        REALISTIC_DIR,
        "pfts_GFDL_regridded.nc",
        "conservative_normed",
    )
    pfts_GFDL_coarse = require_var(
        xr.open_dataset(pfts_gfdl_regridded), "FPC_PFT", str(pfts_gfdl_regridded)
    )

    # Historical LPJ-GUESS distribution, regridded to CLM grid.
    pfts_hist = DataArray_from_LPJGUESS(
        str(LPJ_HIST_PATH),
        name="FPC_PFT",
        colnames=False,
        da_attrs=pfts_CLM,
        main_attrs={"long_name": "foliage projective cover (fraction of gridcell)"},
    ).isel(natpft=slice(0, 16))

    pfts_hist_tmp = REALISTIC_DIR / "pfts_hist.nc"
    pfts_hist.load().to_netcdf(pfts_hist_tmp)
    pfts_hist_regridded = run_regrid(
        pfts_hist_tmp,
        pfts_clm_tmp,
        REALISTIC_DIR,
        "pfts_hist_regridded.nc",
        "conservative",
    )
    pfts_hist_coarse = require_var(
        xr.open_dataset(pfts_hist_regridded), "FPC_PFT", str(pfts_hist_regridded)
    )

    # Basic structural checks before conversion.
    check_dims_match(pfts_CLM, pfts_GFDL_coarse, "future LPJ regridded PFTs")
    check_dims_match(pfts_CLM, pfts_hist_coarse, "historical LPJ regridded PFTs")

    # Convert LPJ-GUESS PFTs into CLM PFT classes.
    pfts_GFDL_converted = PFT_convert_LPJGUESS_to_CLM(
        CLM_pfts=pfts_CLM, LPJGUESS_pfts=pfts_GFDL_coarse
    )
    pfts_hist_converted = PFT_convert_LPJGUESS_to_CLM(
        CLM_pfts=pfts_CLM, LPJGUESS_pfts=pfts_hist_coarse
    )

    target_natpfts = [1, 2, 3, 5, 7, 8, 11, 12]
    assert_subset_natpfts(pfts_CLM, target_natpfts, "CLM PFTs")
    assert_subset_natpfts(pfts_GFDL_converted, target_natpfts, "Converted future PFTs")
    assert_subset_natpfts(pfts_hist_converted, target_natpfts, "Converted historical PFTs")

    # Fix invalid values before differencing.
    pfts_GFDL_converted = sanitize_percentages(
        pfts_GFDL_converted.where(pfts_GFDL_converted.notnull()),
        label="future converted PFTs",
    )
    pfts_hist_converted = sanitize_percentages(
        pfts_hist_converted.where(pfts_hist_converted.notnull()),
        label="historical converted PFTs",
    )

    # Apply the LPJ future-minus-historical change to the CLM baseline.
    change = pfts_GFDL_converted - pfts_hist_converted
    pfts_CLM_GFDL = pfts_CLM.copy().astype(np.float64)

    for n in target_natpfts:
        pfts_CLM_GFDL.loc[dict(natpft=n)] = (
            pfts_CLM_GFDL.sel(natpft=n) + change.fillna(0.0).sel(natpft=n)
        )

    # Keep land cells only, clamp negatives, and renormalize to 100%.
    pfts_CLM_GFDL = pfts_CLM_GFDL.where(lnd_frac > 0)
    pfts_CLM_GFDL = pfts_CLM_GFDL.clip(min=0.0, max=100.0)
    pfts_CLM_GFDL = sanitize_percentages(
        pfts_CLM_GFDL.where(lnd_frac > 0),
        label="final edited CLM PFTs",
    )

    # Final consistency checks.
    final_total = pfts_CLM_GFDL.sum("natpft", skipna=True)
    valid_land = lnd_frac > 0
    if bool(((np.abs(final_total - 100.0) > 1e-4) & valid_land).any()):
        bad = int((((np.abs(final_total - 100.0) > 1e-4) & valid_land)).sum().item())
        raise ValueError(f"Final PFT sum check failed in {bad} land grid cells")

    if bool(((pfts_CLM_GFDL < -1e-10) & valid_land.broadcast_like(pfts_CLM_GFDL)).any()):
        bad = int((((pfts_CLM_GFDL < -1e-10) & valid_land.broadcast_like(pfts_CLM_GFDL)).sum()).item())
        raise ValueError(f"Final negative-value check failed in {bad} cells")

    # Apply modifications to the original surfdata map and save.
    pfts_tot = convert360_180(convert_lsmcoord(dset_in)).PCT_NAT_PFT
    ds_out = surfdatamap_modification(
        original_ds=dset_in,
        pfts_tot=pfts_tot,
        edited_pfts=pfts_CLM_GFDL,
        method="irregular_area",
    )

    ds_out.load().to_netcdf(OUTPUT_PATH)

    # Cleanup temporary files.
    for tmp in [pfts_gfdl_tmp, pfts_clm_tmp, pfts_gfdl_regridded, pfts_hist_tmp, pfts_hist_regridded]:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass

    print(f"Saved modified surfdata file to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
