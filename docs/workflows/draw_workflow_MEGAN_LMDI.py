"""Draw docs/workflows/workflow_MEGAN_LMDI_logic.png: the MEGAN exact-split (LMDI)
workflow, each step with what it does and why. Sources: docs/MEGAN_ATTRIBUTION.md,
cases-scripts/megan-lmdi/README.md, postprocess/megan_lmdi/README.md, docs/CLAUDE_log.md.
Status box = 15 Nov 2026 19:00. Run: $PY docs/workflows/draw_workflow_MEGAN_LMDI.py
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C = dict(run="#2C3990", prep="#5D9A92", check="#B08A1E", watch="#9A4A84",
         out="#777777", prob="#BC423E", status="#DE7A3A", logic="#1F6F66")
FILL = dict(run="#E6E6F2", prep="#EAF1F0", check="#F6F0E2", watch="#F2E7EF",
            out="#EFEFEF", prob="#F6E4E3", status="#FBEDE4", logic="#E3F0EE")

W, LH, PAD = 20.0, 0.205, 0.17          # figure width (in), line height, padding
fig_h = 26.9
fig = plt.figure(figsize=(W, fig_h))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(fig_h, 0); ax.axis("off")


def box(x, y, w, kind, title, what, why=(), fs=10.2):
    """Box with a bold title, 'what' lines (black) and 'why' lines (italic, coloured)."""
    n = 1.4 + len(what) + (0.4 + len(why) if why else 0)
    h = n * LH + 2 * PAD
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=FILL[kind], ec=C[kind], lw=2))
    ty = y + PAD + 0.12
    ax.text(x + 0.2, ty, title, color=C[kind], fontsize=fs + 1.6, weight="bold", va="center")
    ty += 1.4 * LH
    for line in what:
        ax.text(x + 0.2, ty, line, fontsize=fs, va="center"); ty += LH
    if why:
        ty += 0.4 * LH
        for i, line in enumerate(why):
            ax.text(x + 0.2, ty, ("WHY ▸ " if i == 0 else "         ") + line, fontsize=fs,
                    va="center", style="italic", color=C[kind] if kind != "out" else "#444"); ty += LH
    return dict(x=x, y=y, w=w, h=h)


def nxt(*bs):
    """y of the next row: below the lowest box of the previous row."""
    return max(b["y"] + b["h"] for b in bs) + 0.45


def arrow(a, b, side="down", rad=0.0):
    if side == "down":
        p, q = (a["x"] + a["w"] / 2, a["y"] + a["h"]), (b["x"] + b["w"] / 2, b["y"])
    else:  # right
        p, q = (a["x"] + a["w"], a["y"] + a["h"] / 2), (b["x"], b["y"] + b["h"] / 2)
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, lw=1.6,
                                 color="#333", connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- header + legend
ax.text(0.3, 0.45, "Workflow B: MEGAN exact split (LMDI): logic and motivation",
        fontsize=21, weight="bold", va="center")
ax.text(0.3, 0.85, "Scripts: cases-scripts/megan-lmdi/ (branch, launch, watch), postprocess/megan_lmdi/ "
        "(identity, LMDI, replay + swaps, checks).  Design and options: docs/MEGAN_ATTRIBUTION.md (option 1 + 1b).",
        fontsize=10.5, color="#555", va="center")
ax.text(0.3, 1.1, "State + logs: /cluster/work/users/adelez/megan-lmdi/<PD|FUT>/   ·   "
        "Each box: what it does (black) and WHY ▸ it is done that way (italic).",
        fontsize=10.5, color="#555", va="center")
legend = [("logic", "motivation / method"), ("run", "model run"), ("prep", "setup"),
          ("check", "check / validation"), ("watch", "automatic watcher"), ("out", "output files"),
          ("prob", "open problem"), ("status", "status 15 Nov 19:00")]
for i, (k, lab) in enumerate(legend):
    lx = 0.3 + i * 2.45
    ax.add_patch(FancyBboxPatch((lx, 1.38), 0.42, 0.28, boxstyle="round,pad=0,rounding_size=0.04",
                                fc=FILL[k], ec=C[k], lw=1.6))
    ax.text(lx + 0.55, 1.52, lab, fontsize=10, va="center")

L, LW = 0.4, 12.6          # left column
R, RW = 13.4, 6.2          # right column
FW = R + RW - L            # full width

# ---------------------------------------------------------------- 1. problem
b1 = box(L, 2.0, FW, "prob", "1. The problem: the approximate split does not add up",
    ["CLM computes per patch (one PFT in a grid cell) and per 30-min step:  E = ε · γL · γT · γP · γA · γC   (ln E = ln ε + Σ ln γ: exact).",
     "But the history file stores MONTHLY GRID-CELL AREA MEANS of each γ.  Multiplying the means ≠ the mean of the products, and area ≠ emission weighting.",
     "→ residual = weighting + co-variation.  PD isoprene JJA ≥45°N (old chain): residual −9.4 (100·Δln), larger than most factors it should explain.",
     "Toy cell: warming only where there are no leaves → γT map +50 %, emission 0 % → residual −41."],
    ["the factor attribution (LAI vs temperature vs light vs leaf age) is a paper result; a reader cannot be told",
     "'temperature explains +1.5 %' next to an unexplained −9 %.  Spreading the residual over the factors (option 5) would hide it, not remove it."])

# ---------------------------------------------------------------- 2. logic
b2 = box(L, b1["y"] + b1["h"] + 0.45, LW, "logic", "2. The logic: split BEFORE averaging (option 1 = LMDI)",
    ["Write the MEGAN factors for EVERY PATCH at EVERY 30-min step (72 fields, CLM tape 2).",
     "Pair each CTRL patch-step with the LCC one (same grid cell + PFT, same time step).",
     "Per pair: LMDI-I splits E_lcc − E_ctrl into composition (ε, plant cover), γL, γT, γP, γA, γC",
     "exactly and independently of order.  Sum the contributions over patches and steps → monthly maps.",
     "1b (replay): Python copies of CLM's get_gamma_L/A/T/P + Shapley swaps → PHYSICAL drivers:",
     "plant cover, leaf area, canopy light, leaf temperature, incoming light, CO₂ factor."],
    ["two facts make it possible: (i) the fields already exist at patch level in our SourceMod",
     "(only namelist changes: hist_dov2xy=.false.), (ii) CTRL and LCC are NUDGED to the same weather and",
     "time step, so every patch-step has a partner.  1b answers the reviewer question 'how much is LAI,",
     "how much the warmer canopy', not 'how much is γT'."])
b2r = box(R, b2["y"], RW, "out", "Options compared (docs/MEGAN_ATTRIBUTION.md)",
    ["1  patch-level output + LMDI: exact, ~4× slower model",
     "1b offline replay on the same output: exact, physical drivers",
     "2  SourceMod, online emission weights: leaves a 'dispersion' term",
     "3  daily / hourly grid-cell γ: removes only part",
     "4  presentation only · 5 spread residual: not defensible"],
    ["1 + 1b is the only option with no residual;",
     "its cost (≈ 2 % of nn9188k for PD) is affordable."])
arrow(b1, b2); arrow(b2, b2r, "right")

# ---------------------------------------------------------------- 3. 5-day test
b3 = box(L, nxt(b2, b2r), LW, "check", "3. 5-day test (29 Oct, CTRL_PD + LCC_PD branches at 2005-01-01)",
    ["bit-identity with the parent: 30-min SFISOP/SFMTERP, 0 differences;  per patch MEG = k·EPS·Πγ to 10⁻¹⁶",
     "size 0.6 GB/day = 216 GB per run-year;  slowdown ×4 (132 vs 33 s per model day);  first real LMDI split, all checks PASS",
     "found: CLM sets E = 0 when Πγ is outside [0, 100) → its own factor 'cutoff'"],
    ["a go / no-go before spending ~2 % of the allocation: does the branch reproduce the parent, is the product exact,",
     "can the disk and the queue take the output?  It also gave a real CTRL/LCC pair to develop the reduction on."])
b3r = box(R, b3["y"], RW, "logic", "Why BRANCHES, not new runs",
    ["the model is deterministic: a branch from the parent's",
     "restart with extra output = the SAME run, bit for bit,",
     "so the split applies to the parent's results."],
    ["restarting the main runs with tape 2 would cost",
     "≈ 30k core-h and 4.5 TB raw per run."])
arrow(b2, b3); arrow(b3, b3r, "right")

# ---------------------------------------------------------------- 4. branch script + years
b4 = box(L, nxt(b3, b3r), LW, "prep", "4. branch_meganpatch.sh RUN START   (creates + builds one case per chain, never submits)",
    ["parent namelists copied verbatim; refuses to build if XML/namelists differ beyond history/start keys",
     "SLIM output: CAM 30-min + monthly SFISOP/SFMTERP (identity), CLM monthly MEG_*/GAMMA*, tape 2 = 72 fields per patch",
     "nudging met file set to the start date (a branch reads met from met_data_file, not from the parent's date)"],
    ["slim output keeps the 4× slowdown and the disk use down; the namelist guard makes sure the branch can only",
     "differ from its parent in what it WRITES, never in what it COMPUTES."])
b4r = box(R, b4["y"], RW, "logic", "Chains and years (user, 4 Nov)",
    ["parents kept restarts only at 2005, 2010, 2015",
     "→ 3 chains per run: 2000 (hybrid from spin-up),",
     "2005, 2010;  years 2001–02, 2005–06, 2010–11",
     "2000 = spin-up year: identity check only, no split"],
    ["6 years spread over 2001–2014 give the",
     "interannual CI at ≈ 6,800 core-h per run-year,",
     "without regenerating restarts."])
arrow(b3, b4); arrow(b4, b4r, "right")

# ---------------------------------------------------------------- 5. production test
b5 = box(L, nxt(b4, b4r), LW, "run", "5. launch_megan_lmdi.sh test PD   (2 jobs × 30 days from 2005-01-01; passed 5 Nov → PD_test60d.ok)",
    ["two complete months, two month boundaries, a job restart (continuation) and a 2nd archive step",
     "identity Jan + Feb, replay on 30–31 Jan / 1 Feb / 28 Feb / 1 Mar, reduction checks, dry-run delete"],
    ["the 5-day test could not see what breaks only in production: monthly averaging, restarts across jobs,",
     "daily files continuing over a restart.  Cheap (≈ 2,700 core-h) compared with a failed batch."])
b5r = box(R, b5["y"], RW, "watch", "Launcher gates (refuses a batch if…)",
    ["the production test has not passed",
     "an earlier year is not reduced, or failed",
     "years not contiguous within a chain",
     "a chain is not at the batch's first year"],
    ["no year is computed twice or on a",
     "broken chain; failures stop early."])
arrow(b4, b5); arrow(b5, b5r, "right")

# ---------------------------------------------------------------- 6. model runs
b6 = box(L, nxt(b5, b5r), LW, "run", "6. Model runs in 2 batches per period (CTRL + LCC in parallel, 1 model year per job ≈ 14 h)",
    ["batch 1 = 2000 2001 2005 2010     batch 2 = 2002 2006 2011     (each chain continues from its last yearly restart)",
     "st_archive → /cluster/work/users/adelez/archive/<case>/lnd/hist/  (one clm2.h1 tape-2 file per day)",
     "archive_guard.sh reruns failed archive jobs automatically (bad preproc nodes b5203/b5204)"],
    ["batches bound the raw disk peak (~1.3 TB) and let batch 1 be checked (and compared with the approximate",
     "split) before batch 2 is spent.  Chains run in parallel, so the wall time is set by the longest chain."])
arrow(b5, b6)

# ---------------------------------------------------------------- 7. watcher + reduction
b7 = box(L, b6["y"] + b6["h"] + 0.45, LW, "watch", "7. watch_megan_lmdi.sh (every 10 min) → reduce_year_job.sh, one year at a time (≈ 3.5 h, login node)",
    ["starts when BOTH runs of the year have 365/365 tape-2 files (and the parents have that year)",
     "a. check_identity.py: branch bit-identical to its parent (CAM 30-min + monthly, CLM monthly MEGAN fields)",
     "b. reduce_megan_lmdi.py --year Y: LMDI per compound × factor × month × grid cell  +  swaps (megan_swaps.py) per patch pair",
     "c. checks, else exit 1 and nothing deleted: same steps; MEG = k·EPS·Πγ (10⁻¹⁰); Σ terms = ΔE (10⁻¹⁰); unexplained = 0;",
     "    replayed γ = CLM's γ (~10⁻¹⁵); flagged steps < 10⁻³ of |ΔE|",
     "d. raw tape 2: delete / keep (--keep-raw, used for PD) / 'only' for 2000",
     "then: copy result + yearly restarts to NIRD (cp -n + cmp)  →  <label>.ok / .failed / .copied"],
    ["a: if the branch is not the parent bit for bit, the split would describe a different run.  c: the checks prove the",
     "split is exact on every year, not just on the test.  d: raw is ≈ 1 TB per case-chain and /cluster/work purges after",
     "42 days, so it has to be reduced on the fly.  Login node because preproc jobs hung (lmod error, 4 Nov)."])
b7r = box(R, b7["y"], RW, "logic", "LMDI rules (per patch pair)",
    ["match by grid cell + PFT (LCC changes which",
     "PFTs exist: 10,296 matched, ~400 one-run-only)",
     "both emit → LMDI-I (log-mean weights)",
     "one run zero → all ΔE to the factor that is zero",
     "  (absent patch → composition; γL=0 → γL)",
     "Πγ outside [0,100) → 'cutoff'",
     "replay timing: ELAI, LAI240, TV24/240 from t−1"],
    ["each rule keeps the sum exact where",
     "ln 0 would break LMDI."])
arrow(b6, b7); arrow(b7, b7r, "right")

# ---------------------------------------------------------------- 8. outputs
b8 = box(L, nxt(b7, b7r), LW, "out", "8. Outputs: data/processed-data/megan-lmdi/megan_lmdi_<PERIOD>_<YEAR>.nc  (a few hundred MB per year, NIRD)",
    ["E_ctrl, E_lcc, contribution[compound, factor, month, lat, lon]  (8 factors incl. cutoff, unexplained)",
     "pair_*, Ep_ctrl, Ep_lcc, swap4 / swap3[compound, term, month, pair]  (4- or 3-group driver split)",
     "restarts of both cases → BRL-FRST-XPSN_archive/<case>/rest/"],
    ["everything is additive: sum over cells × area and months, then 100·Δln E · C_f / ΔE gives each factor's share",
     "in the units of the attribution figures.  Restarts saved so any year can be rerun after the purge."])
arrow(b7, b8)

# ---------------------------------------------------------------- 9. validation
b9 = box(L, b8["y"] + b8["h"] + 0.45, LW, "check", "9. Validation and use (PD, 15 Nov)",
    ["check_reduced_vs_raw.py: all 6 PD years PASS (Jan + Jul, ≤ 10⁻¹⁵); July 2005 re-reduced from raw = bit-identical",
     "megan-lmdi-vs-approx.ipynb: the approximate split has the WRONG SIGN for the main terms.  Isoprene ≥45°N, ANN:",
     "    composition  approx +12.4  vs  LMDI −2.2 ± 0.2;   γL  −3.0 vs +3.4 ± 0.5;   γT  +2.4 vs +0.5;   residual −9.8 hid it",
     "6 years representative (approx split over 6 vs 25 years agree); LMDI CI ≤ 1.1"],
    ["prove the reduced files are a faithful summary of the raw output BEFORE the raw is deleted, and measure how",
     "much the residual mattered.  Result: it was not a small correction; it reversed the story (plan step 8)."])
b9r = box(R, b9["y"], RW, "prob", "Open before raw deletion",
    ["2000-chain (hybrid) days start at 00:00, the",
     "2005/2010 chains at 00:30 → 2001/02 months",
     "shifted by one step (≤ 3·10⁻³ in JJA cells);",
     "re-reduce aligned? (user decision)",
     "raw deletion ON HOLD; purge ~mid-Dec"],
    ["raw is the only way to redo",
     "a reduction."])
arrow(b8, b9); arrow(b9, b9r, "right")

# ---------------------------------------------------------------- 10. status
b10 = box(L, nxt(b9, b9r), FW, "status", "10. Status 15 Nov 19:00 and next",
    ["PD: all 6 years reduced (2001 2002 2005 2006 2010 2011 .ok + .copied), comparison done, methods text filled (PD).",
     "FUT batch 1 (2000 2001 2005 2010) submitted today: 2000 chain running (jobs 1803926/28), 2005 chain queued (1803949–52), 2010 chain building;",
     "watcher + batch-2 waiter alive (batch 2 = 2002 2006 2011 starts when 2001/2005/2010 are .ok).",
     "Next: FUT reductions → FUT comparison + \\NUM in methods → user decides the 2001/02 shift → then raw deletion."],
    ["FUT goes the same gated way as PD, so its numbers are exact and checked the same way."])
arrow(b9, b10)

out = Path(__file__).with_name("workflow_MEGAN_LMDI_logic.png")
fig.savefig(out, dpi=110, bbox_inches="tight", facecolor="white")
print(out, "bottom y =", round(b10["y"] + b10["h"], 2), "of", fig_h)
