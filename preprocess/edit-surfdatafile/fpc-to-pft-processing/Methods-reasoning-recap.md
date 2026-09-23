# Methods reasoning — recap

A plain-language record of *why* the surfdata is built the way it is, and every
decision made along the way. This is the narrative behind the code and the paper
methods; keep it for yourself and co-authors. Status flags: **[settled]**,
**[open]**, **[revised]**.

---

## The goal
Impose the LPJ-GUESS projected boreal vegetation change onto the CLM surface
dataset (`PCT_NAT_PFT`) to run a semi-realistic land-cover-change experiment
(boreal greening → BVOC + snow-albedo feedbacks) under fixed present-day climate.

## The central problem: FPC ≠ PCT_NAT_PFT
LPJ-GUESS reports **FPC** (foliage projective cover) — a light-defined, saturating
cover fraction that mixes a PFT's *area* with its *leaf density*, on the natural
land unit, summing to <1. CLM's **PCT_NAT_PFT** is a pure *area* partition on the
natural-veg land unit, summing to 100% (incl. bare), with density held separately
(LAI is prognostic). So FPC cannot be dropped into PCT_NAT_PFT directly.

## The two datasets **[settled]**
LPJ-GUESS (Tang et al. 2023) provides two per-PFT fields on the same grid/slices:
**FPC** (drives the surfdata) and **LAI** (diagnostic only — never written).
Three leaf-area quantities are kept distinct throughout: LPJ-GUESS FPC ·
LPJ-GUESS LAI · CLM prognostic LAI.

---

## Decisions, with reasoning

### 1. Anomaly, not absolute **[settled]**
Impose future − historical, not the absolute LPJ distribution. Cancels the two
models' shared structural bias (the systematic FPC-vs-CLM offset); transfers only
the projected change.

### 2. FPC is on the natural-land-unit basis **[settled — confirmed by data provider]**
Verified two ways: (a) the accounting identity `Total = Natural_sum·f_nat +
Peatland_sum·f_peat` holds to ~2e-4 while the per-gridcell alternative is off by
~0.21; (b) Jing confirmed the aggregation chain (individual → patch → stand →
gridcell), where the per-PFT value at the **stand** level = the natural land unit,
the same basis as PCT_NAT_PFT. Consequence: `bare = 1 − Σ(natural FPC)`, and
`f_nat` is NOT used in the pipeline (diagnostic only). Peatland is a separate
stand with no CLM equivalent → excluded.

### 3. Use FPC as-is; don't reconstruct crown area **[settled]**
Options weighed:
- raw ΔFPC — mixes in densification, but see #7;
- relative FPCᵢ/ΣFPC — rejected, discards bare (large in Arctic), erases the
  tundra-greening signal;
- reconstruct crown footprint from FPC & LAI — rejected, not uniquely
  identifiable, and would make "area" inconsistent across life forms;
- **chosen: FPC as the distribution currency for all PFTs; CLM regenerates leaf
  density via prognostic LAI.** The density content of FPC is deliberately
  discarded because CLM redoes it.

### 4. PFT correspondence **[settled]**
Matched on growth form + leaf form + phenology; where CLM is coarser, guided by
comparing spatial cover maps. Final scheme: trees 1:1; all shrubs + prostrate
dwarf shrubs → BoBDS; GRT + C3G → aC3; moss/lichen → bare; peatland excluded.
- **GRT → aC3 (grass), not BoBDS (shrub):** decided on growth form (graminoid is
  a grass) and because GRT+C3G maps complement spatially. Note: the spatial proxy
  had leaned shrub; growth form was chosen deliberately, and it is more
  appropriate for the biogeophysics (graminoid has no woody above-snow structure).
- **Phenology caveat:** CLM's only boreal shrub (BoBDS) is nominally deciduous, so
  evergreen shrubs (HSE, LSE) map into it despite the mismatch — no evergreen
  boreal shrub PFT exists in CLM.
- **veg-group table corrected:** EPDS/SPDS are dwarf *shrubs* (not grass); moss is
  *non-vascular* (→ bare).

### 5. Conservation: bare-only closure **[settled — was a real bug]**
The anomaly is built in a closed partition (bare + PFTs sum to 1) so it sums to
zero per cell; adding it preserves the 100% normalization. **Bare ground absorbs
the net change; untouched PFTs never enter the arithmetic** so they stay
bit-identical. (Earlier global renormalization leaked up to 8 pp into untouched
PFTs across 197 cells — fixed.)

### 6. Over-subscribed cells: proportional scaling **[settled; number REVISED]**
Where the imposed expansion exceeds available area (changed PFTs + bare can't fit
under 100% given the fixed untouched PFTs), the positive increments are scaled
down proportionally — preserving the change's relative composition — so the column
closes and bare stays ≥0. **Count from the real run: ~807 cells (~16% of the 4914
land cells)**, not the ~476/10% used in early drafts. 16% is high enough to state
explicitly in the methods.

### 7. FPC adequacy as a distribution proxy **[SETTLED — reframed twice]**
*Evolution of this decision, kept for the record:*
- **v1 (retracted):** "~85–95% colonization." Could not be reproduced; discard.
- **v2 (superseded):** colonization-vs-persistence on the native grid gave
  grid/threshold-sensitive numbers (BoNET ~56%, larch ~18%, shrubs/grasses
  ~79–90%). The flaw: **colonization/persistence is the wrong axis.** Area
  expansion also happens *inside* already-occupied cells (crown footprint
  spreading), which that split wrongly bucketed as "persistence" and made larch
  look densification-dominated.
- **v3 (FINAL):** decompose directly into **area-expansion vs leaf-densification**,
  regardless of prior occupancy — this is the signal we actually care about (keep
  warming-driven area expansion; drop CO2-driven densification, which CLM
  regenerates via prognostic LAI).

*Method (area_vs_densification notebook):* classify each cell by the joint
FPC–LAI response. A cell is **densification** only with the full saturation
signature — material ΔLAI, small absolute ΔFPC, small ΔFPC per unit ΔLAI, and
already-high FPC. All other meaningful +ΔFPC → **area-expansion**. Mutually
exclusive, cos-lat weighted.

*Result (strong, threshold-robust):* meaningful +ΔFPC is overwhelmingly
area-expansion — **BoNET ~99.7%, ~100% for BoNDT/BoBDT/shrubs/aC3**;
densification stays **<5% of +ΔLAI** for every group even under permissive
thresholds, across permissive/primary/strict scenarios.

*Interpretive limit (state it):* grid-cell FPC + grid-cell LAI don't uniquely
determine occupied area vs within-canopy density — diagnostic signals, not an
exact physical decomposition. Unsaturated densification (FPC and LAI rising
together) is counted as area-expansion, so the area share is an **upper bound**;
conclusion still robust. A clean quantitative partition would need within-crown
LAI (lai_ind) — now a footnote, not a blocker, since the result is
threshold-robust.

*Note:* the colonization framing (v2) is retained only as an optional reported
sub-category ("of the area expansion, X% is into wholly new cells"), not the
headline. `colonization_vs_persist.py` is superseded by the
area-vs-densification notebook.

### 8. Seasonal basis (peak vs annual mean) **[open — new data just arrived]**
New monthly climatology (Jing) shows deciduous PFTs swing from ~0 (winter) to a
summer peak (e.g. GRT 0.00 → 0.26), while evergreens are flat. So an *annual-mean*
FPC under-reads deciduous types by up to ~2×; **annual-maximum (peak-month) FPC**
removes this. Deciding whether to switch the pipeline to peak-month FPC.
- **Blocker:** building a peak-based *anomaly* needs the **historical (1970–2000)
  monthly** climatology for GFDL, which was not in the delivery (future only). The
  time series file starts 2015 and is domain-aggregated (no lat/lon) → cannot
  substitute. **Action: request GFDL 1970–2000 monthly FPC & LAI from Jing.**
- Also worth confirming with Jing: is the exported LAI the within-crown `lai_ind`
  (needed for the opacity/larch claim) or gridcell-mean LAI?

---

## What is written where
- **Surfdata provenance attrs:** Tang et al. (2023) [full cite pending], anomaly
  method, n_scaled, only PCT_NAT_PFT edited.
- **Paper methods** (`methods_draft.md` / `.tex`): sections 1–6; §5 needs
  n_scaled=807/~16%; **§6 must be rewritten** per decision #7 (retract 85–95%).
- **Correspondence table:** `figures/pft_correspondence.csv`.

## Open items checklist
- [ ] Request GFDL 1970–2000 monthly FPC & LAI from Jing (blocker for peak-anomaly)
- [ ] Confirm LAI definition (within-crown vs gridcell-mean) with Jing
- [ ] Decide: switch pipeline to peak-month FPC? (pending historical monthly)
- [ ] Finalize colonization numbers: area-weighted, native grid, chosen EPS
- [ ] Rewrite methods §6 to the revised colonization story
- [ ] Fill n_scaled=807 / ~16% in methods §5
- [ ] Full Tang et al. (2023) citation + contact field in provenance
