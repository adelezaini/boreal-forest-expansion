# fBVOC prescription artefact: what it is and how the BVOC effect is measured

Notebooks:

- `diagnostics/fbvoc-prescription-artefact/fbvoc_prescription_artefact.ipynb`: is there an artefact?
- `fbvoc_artefact_causes.ipynb`: why, hypotheses H1–H5. Old-chain PD runs on CTRL land, kept on purpose (user 2026-11-02): the CO₂ bug was in the FUT land spin-up, and both runs of each contrast share land and restart.
- `how_big_artefact_is_PD.ipynb`: does it depend on the land cover?

Evidence tags: **(a)** verified in output, **(b)** inference, **(c)** unverified.

## 1. The problem

The fBVOC runs switch MEGAN off and prescribe all 19 MEGAN species from a 2001–2014 **climatology** of a source run (half-hourly for 8 species, monthly for 11).

Prescribing the emissions changes SOA by itself, even when they are the run's own emissions.

**Old chain, SOA_cb, % of CTRL_PD** (`fbvoc_prescription_artefact_outputs/tables/verdict.txt`) (a):

| Contrast | Meaning | Years | Global | 45–90°N |
|---|---|---|---|---|
| A = CTRL_PD_fBVOCctrlPD − CTRL_PD | artefact (same land, own emissions) | 2001–02 | **+3.03 %** | +2.99 % |
| C = LCC_PD − LCC_PD_fBVOCctrlPD | uncorrected `BVOC_PD` | 2001–02 | −4.89 % | −4.24 % |
| C + A | corrected BVOC effect | 2001–02 | −1.85 % | −1.25 % |

The artefact accounts for 62 % of C globally and 71 % at 45–90°N. Before the artefact run existed, the hint was already there (a): with the same emissions, LCC_PD_fBVOCctrlPD had +3 % SOA vs CTRL_PD in every band, every season and 14 of 14 years.

## 2. Cause (`fbvoc_artefact_causes.ipynb`, old-chain PD runs)

| Hypothesis | Result |
|---|---|
| H1 missing species | **rejected** (a): the 19 prescribed species = `megan_specifier`; coupler fields identical except `Fall_voc*` |
| H2 diurnal timing | **rejected** (a): the prescribed file has the same diurnal phase as the CTRL_PD h1 output |
| H3 emission–weather link | real for the precursors (a): A τ_ISOP +10–28 % at 45–90°N. Not correlated with A SOA_cb (a) |
| H4 SOA budget | production unchanged (−0.02 %); **lifetime +3 %** (7.02 → 7.24 d); the extra SOA is at 400–100 hPa (a) |
| H5 replay with actual yearly emissions (CTRL_PD_fBVOCctrlPD_HR) | R = +0.49 % vs A = +3.03 % → **the climatology is the cause** (a) |

**Mechanism (b):** in the climatology, emissions no longer follow day-to-day weather. For example, they are also released on convective days, lifted, and form SOA higher up, where it lives longer.

## 3. Fixed BVOC ≠ MEGAN off

In an fBVOC run MEGAN's code is off, but the emissions are **frozen**, not zero: realistic amounts, unable to respond to the land or the weather.

Zero emissions would change the oxidant and SOA background. Because the response is nonlinear, the split would then not add up.

In LCC_PD_fBVOCctrlPD the newly forested cells keep CTRL's (tundra/grass) emissions. That is by design.

## 4. Two ways to remove the artefact

**Notation:**

- X_P^E = land X (LCC, CTRL), period P (PD, FUT), emissions E prescribed.
- X_P = interactive MEGAN.
- art_X,P = X_P^xP − X_P (own emissions prescribed − interactive).

**A: prescribed pairs.** Same land, both runs prescribed, only the emissions differ:

$$\text{BVOC}^{A}_{P} = \text{LCC}_P^{\,\text{lcc}P} - \text{LCC}_P^{\,E_\text{ref}}$$

**B: matched baseline.** The interactive contrast plus the artefact measured on CTRL land:

$$\text{BVOC}^{B}_{P} = \left(\text{LCC}_P - \text{LCC}_P^{\,E_\text{ref}}\right) + \text{art}_{\text{CTRL},P}, \qquad \text{art}_{\text{CTRL},P} = \text{CTRL}_P^{\,\text{ctrl}P} - \text{CTRL}_P$$

With E_ref = ctrlP, B gives a closed split:

$$\underbrace{\text{LCC}_P - \text{CTRL}_P}_{\text{total (no artefact)}} = \underbrace{\text{LCC}_P^{\,\text{ctrl}P} - \text{CTRL}_P^{\,\text{ctrl}P}}_{\text{non-BVOC}} + \underbrace{\text{BVOC}^{B}_{P}}_{\text{BVOC}}$$

**Link between A and B:**

$$\text{BVOC}^{A}_{P} - \text{BVOC}^{B}_{P} = \delta_P = \text{art}_{\text{LCC},P} - \text{art}_{\text{CTRL},P}$$

This is exact for absolute changes and first order for % changes. δ_P is the same for every contrast of a period, so differences between contrasts are identical in A and B.

**Naming clash.** In the 30 Oct plan `~/.claude/plans/ok-so-final-decision-mellow-goose.md` and the session logs before 30 Oct 15:49, "option A" means the *matched baseline*, i.e. design **B** here.

**Variant with one twin per emission source** (that plan): it computes BVOC = (LCC_P − CTRL_P) − (LCC_P^E − CTRL_P^E) for each E, with a CTRL twin for every LCC fBVOC run. It needs one CTRL run per source and answers a different question: the forest BVOC effect with emissions fixed at E, not the contrasts in the table below. It still assumes art(LCC land) ≈ art(CTRL land) (see "Where the artefact sits"), so it removes no assumption that B makes. Only the CTRL_FUT_fBVOCctrlFUT twin exists (24e). CTRL_FUT_fBVOCctrlPD and CTRL_FUT_fBVOClccPD were not made: the 30 Oct 16:33 decision kept one FUT baseline.

**Where the artefact sits (b, from H5).** H5 shows that the artefact is the loss of the day-to-day emission–weather covariance of the **interactive** run. A prescribed run X_P^E differs from X_P by two things: (i) the mean emissions, E instead of X's own; (ii) the lost covariance of X_P, ≈ art_X,P whatever E is. So

$$X_P^{E} pprox X_P + 	ext{effect of } (E - E_{X,P}) + 	ext{art}_{X,P}$$

and the artefact belongs to the land/period of the run, not to the prescribed source. One baseline per period therefore corrects every contrast of that period, including PD emissions in FUT weather. Only second-order terms depend on E (e.g. the SOA response to the lost covariance may scale with the emission level) (c).

**Assumptions.** Both designs assume the artefact does not depend on which emissions are prescribed (second order, see above). B also assumes δ ≈ 0, i.e. it does not depend on the land. This is plausible (b), because all runs are nudged to the same winds and pressure; temperature, humidity and convection over the new forest are not nudged.

### Parallel contrasts

| Meaning | A | B |
|---|---|---|
| PD BVOC effect (forest) | LCC_PD^lccPD − LCC_PD^ctrlPD | (LCC_PD − LCC_PD^ctrlPD) + art_CTRL,PD |
| FUT BVOC effect (forest) | LCC_FUT^lccFUT − LCC_FUT^ctrlFUT | (LCC_FUT − LCC_FUT^ctrlFUT) + art_CTRL,FUT |
| Climate-driven emission change, LCC land | LCC_FUT^lccFUT − LCC_FUT^lccPD | (LCC_FUT − LCC_FUT^lccPD) + art_CTRL,FUT |
| Forest + climate | LCC_FUT^lccFUT − LCC_FUT^ctrlPD | (LCC_FUT − LCC_FUT^ctrlPD) + art_CTRL,FUT |

### Pros and cons

| | A | B |
|---|---|---|
| Extra runs | PD 1; FUT 2 (LCC_FUT saves no half-hourly emissions → rerun with `HR_BVOC_ALL` + LCC_FUT_fBVOClccFUT) | PD 1 (CTRL_PD_fBVOCctrlPD); FUT 1 (CTRL_FUT_fBVOCctrlFUT) |
| Assumption | artefact independent of the emission field | also δ ≈ 0 |
| Noise | 2 runs per contrast | 4 runs per contrast (≈ √2 more) |
| Closed split total = non-BVOC + BVOC | no | yes |
| Uses the real interactive LCC run | no | yes |

## 5. Decision (user, 2026-10-30)

**Design B for PD and FUT, plus one design-A run in PD to measure δ_PD:**

$$\delta_\text{PD} = \left(\text{LCC}_\text{PD}^{\,\text{lccPD}} - \text{LCC}_\text{PD}\right) - \left(\text{CTRL}_\text{PD}^{\,\text{ctrlPD}} - \text{CTRL}_\text{PD}\right)$$

If δ_PD is small compared with BVOC_B, B is supported in FUT too. If it is large, design A in FUT is worth its 2 runs.

**Proposed rule** (`how_big_artefact_is_PD.ipynb`; SOA_cb, Global and 45–90°N): R = |δ_PD| / |BVOC_B|.

- R < 0.25 → B is adequate.
- R > 0.5 → A in FUT.
- In between → judgement.

| Run | Script | Years | Role |
|---|---|---|---|
| CTRL_PD_fBVOCctrlPD | 14c | 2000–2014 | art_CTRL,PD |
| CTRL_FUT_fBVOCctrlFUT | 24e | 2000–2014 | art_CTRL,FUT |
| LCC_PD_fBVOClccPD | 14e | 2000–2002 (3-yr test, user OK) | art_LCC,PD → δ_PD |

All three are new-chain runs (`-20261031`), launched and postprocessed by `cases-scripts/auto_launch_new_chain.sh`.

## 6. First new-chain numbers (2026-11-02, SOA_cb, % of the interactive run) (a)

| Artefact | Years | Global | 90–30°S | 30°S–30°N | 45–90°N |
|---|---|---|---|---|---|
| art_LCC,PD = LCC_PD_fBVOClccPD − LCC_PD | 2001–02 | +3.64 (+3.04 / +4.25) | +4.01 | +3.86 | +2.97 (+1.41 / +4.52) |
| art_CTRL,FUT = CTRL_FUT_fBVOCctrlFUT − CTRL_FUT | 2001–14 | +2.78 (SD 1.37) | +3.33 | +2.73 | +2.64 (SD 2.19) |
| art_CTRL,FUT | 2001–02 | +4.76 | +5.17 | +4.79 | +4.85 |

**FUT yearly, global:** +4.3, +5.2, +4.9, +2.4, +2.5, +1.1, +2.9, +2.0, +3.0, +0.8, +2.5, +3.7, +1.4, +2.1 (trend −1.9 %/decade).

- The FUT artefact is larger in the first years, so a 2-year mean is not representative of the 15-year mean.
- δ_PD pairs the same years on both land covers, so a shared early-year excess cancels (b). Check that art_CTRL,PD (CTRL_PD_fBVOCctrlPD) shows the same early-year pattern.
- Do not compare these numbers with the old-chain +3.03 %: different chains.

**Pending:** δ_PD and the verdict, once CTRL_PD_fBVOCctrlPD is postprocessed (`how_big_artefact_is_PD.ipynb`, rerun by hand).

## 7. Caveats

- **BVOC effect = the emission change between LCC and CTRL with interactive MEGAN.** That includes the new vegetation and MEGAN's response to the changed climate. The MEGAN split (`MEGAN_ATTRIBUTION.md`) separates them.
- The non-BVOC part (LCC^ctrl − CTRL^ctrl) includes every land effect not going through BVOC emissions: albedo, evapotranspiration, dry deposition, and possibly dust (c).
- **Never mix chains in one contrast.** All runs of a formula must come from the new chain.
- The 15-year runs (CTRL_PD_fBVOCctrlPD, CTRL_FUT_fBVOCctrlFUT) match the 2001–2014 climatology years. In the old 2-year test, part of A came from 2001–02 not being an average year (A − R = +2.55 % mixes both effects).

## 8. In the paper (Methods)

Outline: `/cluster/home/adelez/boreal-forest-expantion-draft/methods-claude.tex`, section M4 (written 2026-11-02). It uses the notation of §4 (superscript = prescribed emission source).

| Point | Where |
|---|---|
| Frozen, not zero emissions (§3), and why | main |
| Artefact: what it is, one sentence on the mechanism (§2, lifetime +3 %, 400–100 hPa) | main |
| Design B closed split, total = non-BVOC + BVOC (§4) | main |
| Assumptions (artefact independent of the emission source; δ ≈ 0) + δ_PD test and the R rule (§5) | main |
| What the BVOC and non-BVOC terms contain (§7) | main |
| Artefact size, new chain, PD and FUT, yearly FUT series (§6) | SI |
| Cause analysis H1–H5 (§2): old-chain PD runs on CTRL land; say so in one line (CO₂ bug was in the FUT land spin-up) | SI |
| Design A and why B was chosen (§4 pros and cons) | SI |

Still open for the text: δ_PD and R (§5 pending); main FUT emission source (CTRL_PD vs CTRL_FUT, on hold). When §5 or §6 get new numbers, update the yellow `\NUM` boxes in M4.
