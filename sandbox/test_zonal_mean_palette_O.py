"""Style test (user 2026-11-03): zonal-mean ΔT figure of
diagnostics/how-warmer-future-climate-is (cell 18) redrawn with palette O (sandbox/test_palette_picture.py).
Reads the notebook's monthly cache; does not touch the notebook or its outputs."""
import os
os.environ.setdefault('HDF5_USE_FILE_LOCKING', 'FALSE')
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import netCDF4
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from boreal_forest_expansion.plotting.style import set_default_style
set_default_style()

NB = ROOT / 'diagnostics/how-warmer-future-climate-is'
CASES = {'PD': 'NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029',
         'FUT': 'NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028'}
SST_DIR = Path('/cluster/shared/noresm/inputdata/noresm-only/atm/cam/sst')
SST_FILES = {'PD': SST_DIR / 'fice-micom-divocn_sst-micom-dow_NHIST_f19_tn14_20190710_1995-2005_series_version20260209_clim.nc',
             'FUT': SST_DIR / 'fice-micom-divocn_sst-micom-dow_NSSP585frc2_f19_tn14_20191014_2090-2100_series_version20260209_clim.nc'}
OUT = ROOT / 'sandbox/test_palette_picture_outputs'

O = dict(gold='#EBC45C', orange='#DE7A3A', red='#C4524E', plum='#A8559A', navy='#2C3990', teal='#5D9A92')
VARIANTS = {  # ANN, DJF, JJA, ΔSST
    'P1_navy_teal_red_plum': [O['navy'], O['teal'], O['red'], O['plum']],
    'P2_navy_teal_orange_gold': [O['navy'], O['teal'], O['orange'], O['gold']],
}

MON = {p: xr.open_dataset(NB / f'how_warmer_future_climate_is_outputs/cache/{c}_monthly_2001-2014.nc') for p, c in CASES.items()}
hist = next((Path('/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive') / CASES['PD'] / 'atm/hist').glob('*.cam.h0.*.nc'))
with netCDF4.Dataset(hist) as d:
    lat, lon = MON['PD'].lat, MON['PD'].lon
    gw = xr.DataArray(d['gw'][:], dims='lat', coords=dict(lat=lat))
    LANDFRAC = xr.DataArray(d['LANDFRAC'][0], dims=('lat', 'lon'), coords=dict(lat=lat, lon=lon))
AREA, WATER = gw.broadcast_like(LANDFRAC), 1 - LANDFRAC
SEASONS = {'ANN': range(1, 13), 'DJF': (12, 1, 2), 'JJA': (6, 7, 8)}

def season_mean(m, s):  # month-length weighted, yearly, then mean over years (as the notebook)
    sel = m.TREFHT.where(m.month.isin(list(SEASONS[s])), drop=True)
    w = m.days.where(m.month.isin(list(SEASONS[s])), drop=True)
    return ((sel * w).groupby('year').sum() / w.groupby('year').sum()).mean('year')

dmap = {s: season_mean(MON['FUT'], s) - season_mean(MON['PD'], s) for s in SEASONS}
dT_global = pd.read_csv(NB / 'how_warmer_future_climate_is_outputs/tables/fut_minus_pd_by_region.csv',
                        index_col=[0, 1, 2]).loc[('TREFHT', 'ANN', 'global'), 'delta']
SST = {p: xr.open_dataset(f)[['SST_cpl_prediddle', 'ice_cov_prediddle']].load()
          .rename(SST_cpl_prediddle='SST_cpl', ice_cov_prediddle='ice_cov')
          .assign_coords(lat=lat, lon=lon) for p, f in SST_FILES.items()}
DAYS = xr.DataArray([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dims='time')
icefree = (SST['PD'].ice_cov.max('time') < 0.15) & (SST['FUT'].ice_cov.max('time') < 0.15) & (WATER > 0.5)
dsst = ((SST['FUT'].SST_cpl - SST['PD'].SST_cpl) * DAYS).sum('time') / DAYS.sum()

zm = lambda da, w: (da * w).sum('lon') / w.sum('lon')
for name, cols in VARIANTS.items():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for s, c in zip(SEASONS, cols):
        ax.plot(lat, zm(dmap[s], AREA), c=c, lw=1.8 if s == 'ANN' else 1.4, label=f'ΔTREFHT {s}')
    ax.plot(lat, zm(dsst, icefree.astype(float)), c=cols[3], ls='--', lw=1.4, label='ΔSST ann (forcing, ice-free)')
    ax.axhline(dT_global, c='0.5', lw=0.8, ls=':')
    ax.set_xlabel('latitude'); ax.set_ylabel('FUT − PD (K)'); ax.set_xlim(-90, 90); ax.set_xticks(range(-90, 91, 30))
    ax.legend(fontsize=8, frameon=False); ax.grid(alpha=0.3)
    fig.savefig(OUT / f'zonal_mean_dT_{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT / f'zonal_mean_dT_{name}.png')
