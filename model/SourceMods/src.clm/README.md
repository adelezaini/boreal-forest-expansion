# MEGAN activity-factor and emission-factor diagnostics

This directory contains a modified `VOCEmissionMod.F90` for diagnosing the
MEGAN 2.1 emission calculation in CLM/NorESM.

The modification adds compound-specific history fields for the activity
factors used in

```text
E = epsilon * gamma * rho
```

where `epsilon` is the baseline emission factor, `gamma` is the environmental
activity factor, and the escape efficiency `rho` is assumed to be one in this
implementation.

## Compatibility

- Developed against the NorESM CTSM branch/version
  `ctsm5.4.042_noresm_v5`.

## Added history fields

For every compound in `shr_megan_linkedlist`, the SourceMod registers the
following inactive-by-default history fields:

| Field | Meaning | Units |
| --- | --- | --- |
| `EPS_<compound>` | Baseline emission factor actually selected by MEGAN | `ug m-2 h-1` |
| `GAMMA_<compound>` | Total activity factor | `1` |
| `GAMMAP_<compound>` | Light/PPFD activity factor | `1` |
| `GAMMAT_<compound>` | Temperature activity factor | `1` |
| `GAMMAA_<compound>` | Leaf-age activity factor | `1` |

`EPS_isoprene` contains the value returned by `get_map_EF(...)` when
`shr_megan_mapped_emisfctrs` is enabled. Otherwise, and for all other
compounds, it contains
`meg_cmp%emis_factors(patch%itype(p))`. The value is saved after this selection
and before the total-gamma validity check.

The SourceMod also retains these common or special factors:

| Field | Meaning | Units |
| --- | --- | --- |
| `GAMMAL` | LAI activity factor, common to all compounds | `1` |
| `GAMMAS` | Soil-moisture activity factor, common to all compounds; currently fixed at one | `1` |
| `GAMMAC_isoprene` | CO2-inhibition activity factor for isoprene only | `1` |

The existing `MEG_<compound>` fields contain the resulting compound emissions
in `kg m-2 s-1`.

## Patch values and gridcell output

MEGAN calculates `epsilon` and `gamma` for each CLM vegetation patch. The
SourceMod therefore stores the diagnostics at patch resolution internally.
With `hist_dov2xy(1) = .true.`, the CLM history system aggregates each
registered patch field to the two-dimensional grid before writing it.

The resulting `GAMMA_<compound>` field is an area-weighted gridcell diagnostic.


## Known caveats

- SourceMods are not automatically updated when CTSM changes. Always diff this
  file against the exact upstream `VOCEmissionMod.F90` before changing model
  versions.
- The current soil-moisture activity calculation is disabled in the supplied
  source, so `GAMMAS` is hard-coded to one (inherited from original file)
- Missing or invalid total gamma values remain missing rather than being
  carried forward from an earlier timestep.
- `EPS_<compound>` is undefined on patches for which the VOC calculation is not
  performed. Decide whether those patches should be treated as missing or zero
  before using `EPS_*` to construct a whole-gridcell effective gamma.
- The standard CAM `MTERP` tracer combines multiple MEGAN compounds. There is no output available as `GAMMA_MTERP`. Compute in postprocessing.

