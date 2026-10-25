"""Postprocess one NorESM case: raw history files -> one netCDF file per category.

Usage:
    python run_postprocess.py CASE_NAME ALIAS COMPONENT [options]

Required arguments:
    CASE_NAME             Full NorESM case name (directory and file prefix).
    ALIAS                 Short name used in output filenames, e.g. CTRL_PD.
    COMPONENT             Model component: atm or lnd.

Options:
    --categories CAT ...  Categories to process (default: all for the component).
    --tape TAPE           History tape (default: h0; use monthly-mean input).
    --raw-path PATH       Directory containing the case folders.
                          Default: ../../BRL-FRST-XPSN_archive/
    --out-path PATH       Directory for processed files.
                          Default: ../data/processed-data/postprocessing/
    --spinup-months N     Initial monthly records to discard (default: 12).
                          Use 0 to keep all records.
    -h, --help            Show usage and exit.

Available categories:
    atm: BVOC SOA SULFATE AEROPT CLOUDPROP RADIATIVE CHEM METEO
    lnd: LAND ENERGY SNOW BIOGEOCHEM BVOC ET QA

Output filenames:
    <ALIAS>_<COMPONENT>_<CATEGORY>_<firstyear>-<lastyear>.nc

Notes: Time coordinates are set to the midpoint of their time bounds.

Example:
    python run_postprocess.py \
        NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 CTRL_PD atm \
        --categories BVOC SOA CLOUDPROP RADIATIVE \
        --raw-path ~/work/archive \
        --out-path ./processed-data/postprocessing \
        --spinup-months 12
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from boreal_forest_expansion.postprocess import run, variables

# Edit these once for your setup (or override on the command line).
RAW_PATH = "../../BRL-FRST-XPSN_archive/"                       # contains <casename>/<atm|lnd>/hist/
OUT_PATH = "../data/processed-data/postprocessing/"
SPINUP_MONTHS = 12


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("casename", help="NorESM case name (directory and file prefix)")
    parser.add_argument("alias", help="short name used in output file names, e.g. CTRL_PD")
    parser.add_argument("component", choices=list(variables.CATEGORIES), help="atm or lnd")
    parser.add_argument("--categories", nargs="+", default=None,
                        help="subset of categories (default: all for the component)")
    parser.add_argument("--tape", default="h0", 
                        help="history tape (default: h0); must contain monthly means, otherwise the run stops with an explanation")
    parser.add_argument("--raw-path", default=RAW_PATH)
    parser.add_argument("--out-path", default=OUT_PATH)
    parser.add_argument("--spinup-months", type=int, default=SPINUP_MONTHS)
    parser.add_argument("--skip-existing", action="store_true",
                        help="skip categories whose output file already exists")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    files = run(args.casename, args.alias, args.component, args.raw_path, args.out_path,
                tape=args.tape, categories=args.categories, spinup_months=args.spinup_months,
                skip_existing=args.skip_existing)
    print("\n".join(files))


if __name__ == "__main__":
    main()
