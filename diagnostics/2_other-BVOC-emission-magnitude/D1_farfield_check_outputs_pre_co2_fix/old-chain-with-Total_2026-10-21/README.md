# D1 with the Total (LCC − CTRL) contrasts: old spin-up chain (record, 2026-10-21)

Kept on purpose (user 2026-10-28) as the record of the set-up problems found with the old chain.
They are not produced by the current `D1_farfield_check.ipynb`, which dropped the Total contrasts on 2026-10-22.

| File | Content |
|---|---|
| `D1_farfield_verdict.csv` | verdict per contrast/term, including `Total_PD`, `Total_FUT` |
| `D1_farfield_regional_stats_with_Total_2026-10-21.csv` | regional stats including the Total contrasts |
| `D1_contributions_total.png`, `D1_maps_total.png` | the matching figures |

**Runs:** CTRL `-20260925` (2001–2009) vs LCC `-20261005`, both from the old chain:
LCC had an extra 100-yr land-only spin-up and CTRL did not; the FUT land-only spin-up ran at 284 ppm CO₂.
Main finding: a tropical `Total_FUT` net-TOA contribution of +0.25 W m⁻², far from any land-cover change,
attributed (inference) to the spin-up mismatch. See
`diagnostics/check-simulation-equilibrium/check-CO2-bug-in-spinups/` (old chain) and
`check-equilibrium-after-co2-fix/` (new chain: unmodified-land LCC − CTRL now within noise).

To do: recompute Total in D1 on the CO₂-fix chain once its nudged runs are archived and postprocessed.
