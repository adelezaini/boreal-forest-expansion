# BOREAL-FOREST-EXPANSION: instructions for Claude

## Project
Code for the paper "Climatic impacts of the Arctic expansion of boreal forests".
- **Model:** NorESM2.3 (`~/NorESM2.3_beta01`): CAM `tropstratchem` + CLM (ctsm5.4), resolution `f19_f19`, nudged. It runs on **Betzy** (project `nn9188k`); data live on **NIRD** (`NS9188K`).
- **LCC (land-cover change):** CLM surfdata whose PFTs come from LPJ-GUESS forced by GFDL-ESM4 under SSP5-8.5 for 2100. It differs from CTRL only in `PCT_NAT_PFT`, at 46–82°N.
- **fBVOC:** MEGAN is switched off (`megan_specifier=''`) and ISOP and MTERP are prescribed from a CTRL_PD half-hourly climatology. **Both** PD and FUT fBVOC runs use this PD climatology; for FUT only the dates are relabelled to 2100 (`preprocess/bvoc-emissions/create_bvoc_emissions_for_year_2100.sh`). See Contrasts for what this means. These existing runs carry the suffix `_IM` (ISOP+MTERP only).
- **Planned all-species fBVOC (decided 2026-10-22):** all 19 MEGAN species prescribed (8 short-lived half-hourly, 11 monthly; 2001–2009 climatology) from reruns of CTRL_PD/CTRL_FUT that use `cam_diagnostics HR_BVOC_ALL`. Aliases: `LCC_PD_fBVOC_PD`, `LCC_FUT_fBVOC_FUT`. Alias suffix `_fBVOC_<SOURCE>` = the run the prescribed emissions come from.
- **Periods:** PD (`NF2000…`, nudged 2000–2009) and FUT (`NF2100ssp585…`).

## Layout
| Path | What |
|---|---|
| `cases-scripts/` | One script per NorESM case. They `source cases-setup.sh`, a shell function library (`set_project_noresm_res_vars`, `prepare_restart_files`, `forcings_2000`, `setup_nudging_data`, `cam_diagnostics`, `clm_diagnostics [fBVOC]`, `install_clm_sourcemods`, `prescribed_bvoc_emissions`, `extend_case`, …). `tests/` = short model test runs, not code tests. `sandbox/` = old. |
| `cases-scripts/bypass_isoprene_diurnal_adjustment.py` | Patches the case's `SourceMods/src.cam/mo_srf_emissions.F90` to skip CAM's isoprene diurnal rescaling. The prescribed half-hourly ISOP already contains the diurnal cycle. Used in the fBVOC cases. |
| `model/SourceMods/src.clm/VOCEmissionMod.F90` | Adds CLM history fields `EPS_*`, `GAMMA*_*` (MEGAN ε and γ factors). Inactive by default; added via `clm_diagnostics`. |
| `preprocess/` | `edit-surfdatafile/` (LPJ-GUESS FPC → CLM PFT → LCC surfdata), `bvoc-emissions/` (CTRL_PD h1 SFISOP/SFMTERP → 365-day climatology `ems_<case>_<y0>-<y1>_<VAR>.nc`; `_for_year_2100.sh` re-stamps the files for FUT), `cplhist-processing/` (cplhist forcing for the land-only spin-ups), `nudging/` |
| `postprocess/` | Raw history files → per-category processed NetCDF (see Commands). `prep/` = NCO variable selection and h0 metadata CSVs. |
| `src/boreal_forest_expansion/` | Python package. `core/` (coordinates, landunit → gridcell, fitting), `postprocess/` (`pipeline.run`, `variables.CATEGORIES`, `derived`, `units`), `analysis/` (`regions.load_modified_cells`, `stats`: cell-wise t-test + FDR), `diagnostics/` (`radiative_forcing`), `plotting/` (`forcing_maps`, `megan_maps`, `maps`, `palette`, `style`), `datasets/`, `preprocess/`. `TBD/` = old code. |
| `analysis/` | Paper notebooks: `forcing_maps.ipynb`, `megan_factor_maps.ipynb` |
| `diagnostics/` | Folders of notebooks and scripts, **not packages**: equilibrium checks, `other-BVOC-emission-magnitude/` (`D1_farfield_check.ipynb`, `D2_megan_budget.ipynb`: self-contained, no `src` import; their outputs go to `D1_farfield/` and `D2_megan_budget/`, each with `figures/`, `tables/` and `logs/`), fincl variable checks, history-file size tests. This is the current layout, not the target; see Code conventions. |
| `results/` | `tables/` (`logs/` holds run logs and `run_nb.py`), `figures/` (current). `figures2-4`, `figures-*` = older figure sets. |
| `data` | Symlink to `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data` (large; don't `find` or `grep` in it). |
| `_old/`, `to-clean/`, `sandbox/` | Legacy. Ignore unless asked. |
| `docs/` | Session logs (see below). |

## Simulations
Script numbering (`cases-scripts/README.md`): first digit **1** = PD, **2** = FUT. Second digit = step (step 1 must finish before step 2). Letter = runs that can go in parallel. `x` = quick preliminary spin-ups. 3x/4x = extra FUT variants.

| Label (used in code/output) | Script | Case name |
|---|---|---|
| `CTRL_PD` | 13a | `NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925` |
| `LCC_PD` | 14a | `NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005` |
| `LCC_PD_fBVOC_PD_IM` | 14b | `NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261008` |
| `CTRL_FUT` | 23a | `NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20260925` |
| `LCC_FUT` | 24a | `NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005` |
| `LCC_FUT_fBVOC_PD_IM` | 24b | `NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261009` |
| `LCC_PD_fBVOC_PD` (planned) | 14b rerun | not yet run |
| `LCC_FUT_fBVOC_FUT` (planned) | new | not yet run |

- **Spin-up chains:** CTRL = 20 yr coupled spin-up (11/21). LCC = CTRL restart → 100 yr land-only BGC spin-up (12b/22b) → 20 yr coupled spin-up (13b/23b). fBVOC starts from the LCC restart.
- **Contrasts** (`plotting/forcing_maps.BVOC_PAIRS`, D1/D2):
  - **Total = LCC − CTRL**, same period: `Total_PD`, `Total_FUT`.
  - **BVOC = LCC − LCC_fBVOC_\***: `BVOC_PD`, `BVOC_FUT`. How to read it:
    - `BVOC_PD` = response to replacing the prescribed CTRL_PD ISOP/MTERP with interactive emissions in the PD LCC setup.
    - `BVOC_FUT` mixes the effect of the future background (climate, CO₂) and the effect of the land-cover change, both measured against CTRL_PD emissions. **Never call it the forest-expansion-only BVOC effect.**
    - Turning MEGAN off also removes the other MEGAN compounds (fBVOC output has no `MEG_*`), so the contrast is not ISOP + MTERP only. Check which emissions differ before attributing a result.
    - Even with a matching reference, a prescribed climatology differs from interactive emissions (no interannual or weather coupling).
  - D2 also uses `LCC_FUT-CTRL_PD`.
- The first 12 months of every nudged run are dropped as spin-up (`--spinup-months 12`).
- The first spin-ups started at year 0001 instead of 0000, so their restarts are dated `0021-01-01` (`NOTES.md`).

## Environment & commands
- **Python:** `PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python` (`$PY` below).
  - `src/` is not reliably installed. Scripts and notebooks do `sys.path.insert(0, …/"src")`; from the repo root, use `PYTHONPATH=src`.
  - nbformat is not available.
  - `setup.sh`, `requirements.txt` and `environment_toupdate.yml` are stale and don't describe the env that is actually used.
- **Postprocess one case:**
  ```
  $PY postprocess/run_postprocess.py CASENAME ALIAS {atm,lnd} [--categories BVOC SOA ...] [--tape h0] [--spinup-months 12] [--skip-existing]
  ```
  - Categories: atm `BVOC SOA SULFATE AEROPT CLOUDPROP RADIATIVE CHEM METEO`; lnd `LAND ENERGY SNOW BIOGEOCHEM BVOC ET QA` (`src/.../postprocess/variables.py`).
  - Input: `~/BRL-FRST-XPSN_archive/<case>/<atm|lnd>/hist`, a symlink to the NIRD archive.
  - Output: `data/processed-data/postprocessing/<ALIAS>_<atm|lnd>_<CAT>_<y0>-<y1>.nc`.
- **Postprocess all 6 cases:** `bash postprocess/run_all_parallel.sh [njobs]`. `njobs` is a positional argument (default 24). The interpreter comes from the `PYTHON` env var, which defaults to the path above. It runs through `xargs -P` with one job per case × component × category, skips outputs that already exist, and writes logs to `<out>/logs/`. `run_all_postprocessing.sh` is the serial version.
- **Run a notebook headless:** `$PY results/tables/logs/run_nb.py path/to/nb.ipynb [expr ...]`. It runs the code cells with the Agg backend from the notebook's own directory.
- **NCO:** `module load NCO/5.2.9-foss-2024a` (as used in `postprocess/prep/select_concat_cam_raw_output.sh`).
- **Model cases:** `bash cases-scripts/<NN>-….sh` creates, builds and **submits** a case (`case.submit`, queue `normal`). Never run one without the user's explicit OK.
- There are no unit tests and no linter.

## Key paths (Betzy / NIRD)
- Archive per case: `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/<case>/`, containing:
  - `rest/` (restarts);
  - `cpl/hist` (land-only forcing);
  - `atm/hist`, `lnd/hist` (raw output).
- Live model archive: `/cluster/work/users/adelez/archive/<case>`. Case dirs: `~/cases/BRL_FRST_XPSN/<case>-<date>`.
- Restarts staged in `~/restart/`; original spin-up initial files in `/cluster/projects/nn9188k/adelez/restart`.
- LCC surfdata: `/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc`.
- Prescribed BVOC: `/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/`.

## Science gotchas (details in `docs/CLAUDE_log.md`)
These are working hypotheses and known facts as of 2026-10-22, not settled conclusions. Re-check them before building on them.
- **Spin-up mismatch: a potential confound in LCC − CTRL. Not isolated (b).**
  - CTRL and LCC have different spin-up histories (a): LCC has the extra 100-yr land-only spin-up.
  - Evidence that it matters (a):
    - the namelists differ only in `fsurdat`, `finidat` and `ncdata`;
    - the surfdata differ only at 46–82°N;
    - yet the tropics (30°S–30°N, 9-yr means) show LCC − CTRL TOTVEGC +10 % in PD, and a D1 `Total_FUT` tropical contribution of +0.25 W m⁻² (net TOA, `diagnostics/other-BVOC-emission-magnitude/D1_farfield/tables/D1_farfield_verdict.csv`).
  - Attributing that tropical signal to the spin-up is inference (b); its size has not been separated from other causes.
- **LCC and fBVOC share the LCC restart**, so this particular mismatch should largely cancel in the BVOC contrast (b). This does not show that the runs have re-equilibrated after the emission change.
- When quantitative findings go into docs, state the variable, region, period, calculation and output file.
- `SF*` = everything the atmosphere receives (MEGAN + prescribed); `MEG_*` = the interactive MEGAN part only (absent in fBVOC).
- Grid-cell `GAMMA_*` is an **area mean** over vegetated patches, not an emission-weighted value. `EPS`/`GAMMA` exist for only 7 of the 21 MTERP compounds.

## Data checks (before any comparison or aggregate)
- Before subtracting fields, check that coordinates, calendar (`noleap`), time coverage, units and spatial basis match. Never silently align away a mismatch.
- CLM fractions differ: grid cell vs land vs natural vegetation vs PFT. Look alike ≠ equivalent.
- Time means weighted by month length; spatial means and totals by cell area × the right fraction.
- Spin-up months are dropped in both `postprocess/pipeline.py` and `analysis/loading.open_cam_monthly`. Drop them **once**: don't feed processed files to the loader.
- Existing output files are not proof of completeness or compatibility. Record input cases, years and processing choices, and keep metadata.
- Never present unexecuted code as tested; say what was actually checked.

## Working style
- The user wants: short labelled sections, tables, bold key terms, worked examples.
- Be critical, and separate facts from inference using evidence tags **(a)** verified / **(b)** inference / **(c)** unverified.

## Code conventions
- Keep task-specific diagnostic calculations and their explanations together in self-contained notebooks.
- Move a function to `src/` only if it has a clear reuse beyond the current diagnostic. Don't create modules just to shorten a notebook.
- No notebook-generator scripts unless explicitly asked.
- Prefer small, focused changes and compact, readable code.

## Data safety
- **Protected** (explicit OK needed to modify or delete): raw history files, restarts, cplhist/nudging forcing, surfdata, prescribed-emission inputdata, anything under `BRL-FRST-XPSN_archive/` or `/cluster/shared/noresm/`.
- **Regenerable** (e.g. `data/processed-data/`, `results/`): regenerate when asked, but avoid overwriting unrelated outputs.
- Before expensive processing, run on a small sample first and estimate the time and memory needed.

## Session logs (mandatory, every prompt)
Two logs in `docs/`, both updated **before ending every turn**:

| File | Reader | Content |
|---|---|---|
| `docs/CLAUDE_log.md` | Claude (cold restart) | `## NOW` at the top, overwritten every turn: active task, exact next action, decisions waiting on the user, uncommitted files, gotchas. Dense: paths, numbers, evidence tags (a) verified / (b) inference / (c) unverified. Below it: dated blocks. |
| `docs/CLAUDE_log_human.md` | Humans | "Where things stand" box at the top, rewritten every turn. Below it: dated blocks with **Goal / Done / Found / Open-next / Files changed**. Plain language, very short, numbers where they matter. |

**Blocks = one per prompt-cache window.**
- A new block starts with a new session or after more than 60 min without prompts. It goes on top (newest first).
- Within a window, **rewrite your own block in place** (the one whose header has your session id, which may not be the top one if sessions run in parallel). **Never append** prompt-by-prompt, and never edit another session's block.
- Header: `## YYYY-MM-DD · HH:MM → HH:MM (N min) · session <id8>`. Keep the end time and duration current.
- Older blocks are never edited, except to fix the end time of the block just closed.
- **Human log keeps the history of open items.** Never delete an Open item from an older block. When one gets done, list it under **Done** in the current block with where it was opened, e.g. `- CTRL re-spin-up done (open since 2026-10-21)`. If an item is opened and closed inside the same block, keep it under Done; don't drop it.

The hook `~/.claude/hooks/boreal_log.py` (registered in `~/.claude/settings.json`) says NEW or CONTINUE BLOCK with times at each prompt. It also blocks the end of the turn if the logs were not touched. If the hook is silent, apply the same rules by hand (`date`).

Trivial turns: only refresh the end time and duration.
End every reply with one line: `📝 Logs updated (block HH:MM → HH:MM)` or `📝 New log block started HH:MM`.
