# analysis-2001-2019: temporary 2001–2019 set (meeting Mon 9 Nov 2026)

Self-contained. **Delete the whole folder when done** (`rm -rf analysis-2001-2019`); nothing else in the repo depends on it or was changed for it.

| Path | Content |
|---|---|
| `cases.txt` | the 11 nudged runs (alias, case name), same cases as the 2001–2014 set |
| `prepare.sh` | does everything below; rerun-safe (skips processed files that exist) |
| `raw-links/` | symlinks to the h0 files **2000-01 … 2019-12** in `/cluster/work/users/adelez/archive` (240 per case and component; the runs keep adding 2020+ files there, the links keep them out) |
| `processed/` | `<ALIAS>_<atm|lnd>_<CAT>_2001-2019.nc`, all 19 categories (year 2000 dropped as spin-up); per-job logs in `processed/logs/` |
| `radiative_forcing_2001-2019.ipynb` | copy of `analysis/radiative_forcing.ipynb` for 2001–2019, executed in place |
| `results/figures/`, `results/tables/` | its outputs (same sub-folders as `results/`) |
| `logs/prepare.log` | log of `prepare.sh` |

Repo code used unchanged: `postprocess/run_all_parallel.sh` (with `RAW_PATH`, `OUT_PATH`, `CASES` overrides), `src/boreal_forest_expansion/`, `results/tables/logs/run_nb_inplace.py`.

Not included: **LCC_FUT_fBVOClccFUT** (24g, design A). It started 6 Nov 20:51 and reaches 2019 only after the meeting; the notebook adds its row by itself if `processed/LCC_FUT_fBVOClccFUT_atm_RADIATIVE_2001-2019.nc` exists (add it to `cases.txt` and rerun `prepare.sh`).

Caveat: the raw links point to the work archive, which purges files after 42 days. The processed files do not depend on the links once made.
