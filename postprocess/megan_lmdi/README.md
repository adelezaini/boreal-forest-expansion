# MEGAN exact split (LMDI) — reduction of the patch-level branch output

Option 1 of `analysis/MEGAN_ATTRIBUTION.md`: the MEGAN emission change LCC − CTRL split exactly into composition, γL (LAI), γT (temperature), γP (light), γA (leaf age) and γC (CO₂, isoprene), with no residual.

## Input

The CLM tape-2 files (`<case>.clm2.h1.<date>.nc`, one per day) of a **CTRL and an LCC branch run covering the same days**: 72 MEGAN fields per patch (PFTS), every 30-min step, instantaneous. They are written by branch runs set up like `cases-scripts/tests/13a-…-meganpatch-5day.sh` (CTRL) and `14a-…-meganpatch-5day.sh` (LCC). Files are read from `/cluster/work/users/adelez/archive/<case>/lnd/hist`, or from the run directory if not archived yet.

## Run

```
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
$PY postprocess/megan_lmdi/reduce_megan_lmdi.py --ctrl <CTRL branch case> --lcc <LCC branch case> \
    --label PD_2005 [--year 2005] [--lat-min 45] [--out data/processed-data/megan-lmdi] [--delete-raw | --delete-dry-run]
```

- One call per year pair (CTRL_Y + LCC_Y). Speed: ≈ 31–37 s per model day with the swaps (≈ 3.5 h per year) on a login node.
- `--delete-raw` deletes both runs' tape-2 files **only if all checks pass**. Without it nothing is deleted.

## Output

`<out>/megan_lmdi_<label>.nc`, a few hundred MB per year:

| Variable | Dimensions | Content |
|---|---|---|
| `E_ctrl`, `E_lcc` | compound, month, lat, lon | mean MEGAN emission of the matched vegetated patches ≥ `lat-min` (kg m⁻² s⁻¹ per grid-cell land area) |
| `contribution` | compound, factor, month, lat, lon | exact contribution of each factor to `E_lcc − E_ctrl`; summed over factors it equals that difference |
| `nsteps`, `month`, `area` | | time steps per month, YYYYMM, grid-cell area (km²) |

Compounds: isoprene and the 7 monoterpenes with MEGAN output. Factors: `composition`, `gammaL`, `gammaT`, `gammaP`, `gammaA`, `gammaC`, `cutoff` (CLM sets the emission to 0 when the total γ is outside [0, 100); the γ responsible is not saved), `unexplained` (must be 0).

All terms are additive: sum them over cells (× area) and months, then 100 · Δln E_region · C_f / ΔE_region gives the factor's share in the units of the attribution figures (100 · Δln ≈ %).

## Method

See the docstring of `reduce_megan_lmdi.py` and `analysis/MEGAN_ATTRIBUTION.md` (option 1). In short:
- Patches are matched by **grid cell + PFT**: the patch lists of CTRL and LCC differ, because LCC changes which PFTs are present.
- Both runs emit: LMDI-I, exact and order-free.
- One run emits zero: the whole change goes to the factor that is zero there (absent patch → composition; e.g. γL = 0 in winter → γL).

## Checks (the script stops, exit 1, nothing deleted, if one fails)

| Check | Tolerance |
|---|---|
| Same time steps in both runs, file by file | exact |
| (grid cell, PFT) unique among vegetated patches | exact |
| Per patch and step, `MEG` = k · `EPS` · product of the γ's | 10⁻¹⁰ relative |
| Per grid cell and month, Σ contributions = `E_lcc − E_ctrl` | 10⁻¹⁰ relative to max E |
| `unexplained` = 0 | 10⁻¹⁰ relative to max E |

## Tests (29 Oct 2026)

- Unit tests of `lmdi()`: toy cell (γT contribution exactly 0), random data (closure to 10⁻¹⁴), absent patch → composition, γL = 0 → γL, missing value → unexplained.
- CTRL 5-day test vs itself: all checks pass, all contributions 0, 47 s for 5 days.
- Real pair (CTRL + LCC 5-day branches, old chain, 2005-01-01 to 01-05): 10,296 patches matched, 427 only in CTRL, 351 only in LCC; all checks pass (product 8.9 × 10⁻¹⁶, closure 9.0 × 10⁻¹⁶, unexplained 0); 99 s. The first run found one patch-step (out of 683 one-run-zero cases) hit by CLM's γ-range safeguard (`VOCEmissionMod.F90:644`): it now goes to `cutoff`. Result (≥ 45°N, area-weighted, 5 winter days, not meaningful yet): isoprene 100·Δln E = +5.94 = composition −3.77 + γL +8.03 + γT −0.10 + γP +1.70 + γA +0.12 + γC −0.04; monoterpenes +1.31 = −2.91 + 4.03 + 0.17 + 0.02 + 0.00 + 0.00 (exact, no residual).

## Replay (option 1b): `megan_replay.py` (2026-11-02)

Python copies of CLM's `get_gamma_L/A/T/P` (`model/SourceMods/src.clm/VOCEmissionMod.F90`), class constants from `megan21_emis_factors_78pft_c20161108.nc` (float32 values, as CLM reads them). Validate: `$PY postprocess/megan_lmdi/megan_replay.py <tape-2 files>`.

**Validated on the 5-day pair** (both runs, all vegetated patches, 10 files): every γ (L, A, T, P) of the 8 compounds = CLM's to ≤ 9 × 10⁻¹⁶, with this **timing**:
- CLM updates ELAI and the running means (LAI240, TV24, TV240, FSUN24/240, FSD/FSI 24/240) **after** VOCEmission in the same step, so the tape holds what MEGAN uses at the **next** step. The replay of step t takes ELAI, LAI240, TV24, TV240 from step t − 1, and TV, FSUN, PAR_* from step t. Step 1 of a daily file needs the last step of the previous file.

**Stale PAR fields.** The SourceMod writes `PAR_*`, `TOPT`, `EOPT`, `ALPHA` only inside the isoprene branch (`imeg == 1`) and only when the isoprene γ passes CLM's safeguard (0 ≤ γ < 100). Where it fails, these fields keep an old value.
- Cause found: on these patch-steps the isoprene **γA is negative** (−0.09 to −4 × 10⁻⁵): CLM estimates last step's LAI as 2·LAI240 − ELAI, which is negative when LAI rises fast, and the isoprene leaf-age weights (Anew = 0.05) then extrapolate below 0. Monoterpenes (Anew = 2) stay valid.
- Size: worldwide 7.3 % of monoterpene patch-steps (mostly crops); **≥ 45°N: 0.02 % (CTRL) / 0.04 % (LCC), 0.001 % of the monoterpene emission, only PFT 13 (C3 non-arctic grass), one row at 48.3°N** (5-day test, January).
- Recoverable exactly: PAR24/240 = (FSD + FSUN·FSI)·4.6 from the previous step's FSD/FSI/FSUN 24/240 (difference 0); instantaneous PAR from the grid-cell direct/diffuse light, derived from any valid patch of the same cell (≤ 10⁻¹⁴); every stale step ≥ 45°N had one.

## Driver swaps (option 1b): `megan_swaps.py` (2026-11-06)

Inside the reduction (user decision 6 Nov 17:55: inside the per-year reduction; per matched patch pair, monthly; all 8 compounds; batch 2 waits for validation on the 60-day test). Method in the docstring of `megan_swaps.py`; in short, per patch pair, step and compound:

ΔE = plant cover (M̄ · Δw) + CO₂ factor (γC, CLM's own) + emission factor (0 for a matched pair) + **Shapley values of the replayed γL·γA·γP·γT over the driver groups** (scaled by w̄ · ā) + replay residual (≈ round-off).

| Groups | Terms (`terms4` / `terms3`) |
|---|---|
| 4 | `plant_cover, leaf_area, canopy_light, leaf_temperature, incoming_light, co2_factor, emission_factor, clm_safeguard, replay_residual` |
| 3 | `plant_cover, canopy, leaf_temperature, incoming_light, co2_factor, emission_factor, clm_safeguard, replay_residual` (canopy = leaf area + canopy light as one group, its own Shapley game) |

- Patch absent or weight 0 in one run → whole ΔE to `plant_cover`; CLM safeguard (γ outside [0, 100)) in either run → `clm_safeguard`.
- **Flagged steps** → whole ΔE to `replay_residual`: the first step of a chain (its previous step is not on the tape), a cell without a patch to derive the light from, or a non-finite replayed value. Reported, must be < 10⁻³ of |ΔE|.
- Timing as in the replay section; the previous step is carried across daily files, and for the first file it is read from the file before it if that exists (e.g. 2010-06-30 for a July start).
- Grid-cell light now (direct, diffuse) is derived by inverting CLM's PAR formula at the patches with fresh `PAR_*` and FSUN < 1; PAR is then rebuilt for every patch, so the stale steps are repaired.

**New output variables** (same file `megan_lmdi_<label>.nc`; the LMDI variables are unchanged):

| Variable | Dimensions | Content |
|---|---|---|
| `pair_ixy`, `pair_jxy`, `pair_pft`, `pair_lat`, `pair_lon`, `pair_area`, `w_ctrl`, `w_lcc` | pair | the patch pairs (matched + one-run-only), weights (0 = absent), cell area km² |
| `Ep_ctrl`, `Ep_lcc` | compound, month, pair | patch emission integrated over the month (kg per m² of grid-cell land) |
| `swap4`, `swap3` | compound, term, month, pair | exact contributions to `Ep_lcc − Ep_ctrl` (same units); summed over terms = the difference |

Region totals: Σ over pairs of value × `pair_area` × 10⁶ → kg; 100 · Δln E · term / ΔE for the figures' units.

**Tests (6 Nov, before the new script replaced the live one):**

| Test | Replayed G vs CLM | Rebuilt PAR vs CLM | Residual at replayed steps | Flagged share of \|ΔE\| | Time |
|---|---|---|---|---|---|
| 60-day pair, first 3 days | 1.1 × 10⁻¹⁵ | 8.0 × 10⁻¹⁴ | 6.3 × 10⁻¹⁶ | 6.4 × 10⁻³ (step 1 only) | 33 s/day |
| 2010 pair, 1–3 July (previous step from 30 June) | 1.3 × 10⁻¹⁵ | 2.2 × 10⁻¹³ | 6.7 × 10⁻¹⁶ | 0 | 37 s/day |
| 60-day pair, all 60 days | 1.3 × 10⁻¹⁵ | 2.2 × 10⁻¹³ | 9.8 × 10⁻¹⁶ | 2.6 × 10⁻⁴ (step 1 only) | 31 s/day (31 min) |

All checks pass on the 60 days; the LMDI variables are bit-identical to the earlier LMDI-only file. The new script replaced the live one on 6 Nov 21:15; `megan_lmdi_PD_test60d.nc` rewritten with the swaps.

Plausibility, 1–3 July 2010, ≥ 45°N, 100 · Δln E (3 groups vs LMDI): isoprene +2.68 = plant cover −0.84 (composition −0.73) + canopy +2.90 (γL + γA +2.89) + leaf temperature +0.54 (γT +0.58) + incoming light +0.07 + CO₂ +0.01; monoterpenes +1.30 = −2.07 (−2.02) + 2.63 (2.55) + 0.72 (0.75) + 0.02. In the 4-group split, canopy light (self-shading) is −0.22 for isoprene and −0.01 for monoterpenes.

## Still to do before production

- ~~Replay (option 1b) inside this reduction~~ done 2026-11-06 (section above).
- ~~Batch job wrapper and launcher~~ done 2026-11-04: `reduce_year_job.sh` (sbatch, per year: identity → reduction → delete), `check_identity.py` (branch vs parent, bit for bit: 30-min CAM SFISOP/SFMTERP matched by time value, monthly CAM and CLM MEGAN fields), `--year Y` (one year of a multi-year chain case, archive only) and `--delete-dry-run` here; launcher and watcher in `cases-scripts/megan-lmdi/` (README there).
