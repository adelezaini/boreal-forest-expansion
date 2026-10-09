"""Run once; subsequent notebooks read the saved mask and CSV.

Usage: python build_modified_cells.py --baseline /path/original_surfdata.nc --modified /path/lcc_surfdata.nc --output modified_cells.nc

python build_modified_cells.py --baseline /cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc --modified /cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc --output modified_cells.nc
"""


import argparse
from equilibrium import build_modified_cells

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, help='Original surface file used to make the LCC file')
    parser.add_argument('--modified', required=True, help='LCC surface file')
    parser.add_argument('--output', default='modified_cells.nc')
    parser.add_argument('--tolerance-pp', type=float, default=1e-6)
    args = parser.parse_args()
    if args.tolerance_pp < 0:
        parser.error('Tolerance must be nonnegative')
    build_modified_cells(args.baseline, args.modified, args.output, args.tolerance_pp)
