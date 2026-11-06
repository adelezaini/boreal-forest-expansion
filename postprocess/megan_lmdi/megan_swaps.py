"""Driver swaps (option 1b of analysis/MEGAN_ATTRIBUTION.md): exact, order-free split of the MEGAN emission change
LCC - CTRL of each matched patch pair into plant cover + driver groups (Shapley values) + small exact terms.

Per matched patch pair (same grid cell + PFT), time step and compound, both runs present:
    E = w * K * EPS * gammaC * G,   G = gammaL * gammaA * gammaP * gammaT   (replayed, megan_replay.py)
    dE = Mbar * dw                                   -> plant_cover        (M = E / w, bar = mean of the two runs)
       + wbar * Gbar * K * EPSbar * d(gammaC)        -> co2_factor         (isoprene; CLM's own gammaC, not replayable)
       + wbar * Gbar * K * gammaCbar * d(EPS)        -> emission_factor    (0 for a matched pair: same PFT, same cell)
       + wbar * abar * phi_g, a = K * EPS * gammaC   -> one term per driver group g (Shapley values of G over the groups)
       + rest                                        -> replay_residual    (CLM's dE minus the sum above; ~ round-off)
    Shapley: G is recomputed for all 2^4 = 16 combinations of CTRL/LCC driver groups; phi_g = weighted mean of the
    change when g is switched from CTRL to LCC, over all orders. sum_g phi_g = G(all LCC) - G(all CTRL), exactly.
    4 groups: leaf_area (ELAI, LAI240), canopy_light (FSUN, FSUN24, FSUN240), leaf_temperature (TV, TV24, TV240),
              incoming_light (grid-cell direct + diffuse light now, FSD24/240, FSI24/240).
    3 groups: canopy (= leaf_area + canopy_light as one group), leaf_temperature, incoming_light (own Shapley game).
Other cases (whole dE to one term): patch absent or weight 0 in one run -> plant_cover; present in both but CLM's
safeguard (total gamma outside [0, 100), MEG = 0, GAMMA not saved) in either run -> clm_safeguard.
Flagged steps (whole dE -> replay_residual, reported separately): the drivers of the previous step are not on tape
(first step of a chain), the grid-cell light cannot be derived (no patch with fresh PAR and FSUN < 1), or a
replayed value is not finite.

Timing (validated on the 5-day test, README): MEGAN at step t uses ELAI, LAI240, TV24, TV240, FSUN24, FSUN240, FSD/FSI
24/240 of tape step t-1 (CLM updates them after VOCEmission) and TV, FSUN, the grid-cell light of step t.
Grid-cell light now: CLM's PAR_sun = (solad + FSUN * solai) * 4.6, PAR_shade = (1 - FSUN) * solai * 4.6, inverted at
every patch with fresh PAR_* (isoprene gamma valid) and FSUN < 1; per cell the max over those patches (they agree to
round-off; the spread is checked). PAR is then rebuilt for every patch, which also repairs the stale PAR_* steps.
"""
import math
import numpy as np
from megan_replay import gamma_L, gamma_A, gamma_T, gamma_P

GROUPS4 = ("leaf_area", "canopy_light", "leaf_temperature", "incoming_light")
GROUPS3 = ("canopy", "leaf_temperature", "incoming_light")
EXTRA = ("co2_factor", "emission_factor", "clm_safeguard", "replay_residual")
TERMS4 = ("plant_cover",) + GROUPS4 + EXTRA
TERMS3 = ("plant_cover",) + GROUPS3 + EXTRA
K_UNITS = 1e-3 / 3600.0 / 1e6                        # MEG [kg m-2 s-1] = EPS [ug m-2 h-1] * gamma * K_UNITS
PREV = ("ELAI", "LAI240", "TV24", "TV240", "FSUN24", "FSUN240", "FSD24", "FSD240", "FSI24", "FSI240")
NOW = ("TV", "FSUN", "PAR_sun", "PAR_shade")
DRIVERS = PREV + NOW


def _weights(n):
    f = math.factorial
    return [f(s) * f(n - s - 1) / f(n) for s in range(n)]


W4, W3 = _weights(4), _weights(3)


def cell_light(par_sun, par_sha, fsun, fresh, cell, ncell):
    """Grid-cell direct (solad) and diffuse (solai) visible light [W m-2], (time, cell), from the patches' PAR_*.
    Returns solad, solai and the max relative spread among the patches of a cell (should be round-off)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        ok = fresh & (fsun < 1) & np.isfinite(par_sun) & np.isfinite(par_sha)
        sai = np.where(ok, par_sha / (4.6 * (1 - fsun)), np.nan)
        sad = np.where(ok, par_sun / 4.6 - fsun * sai, np.nan)
    out = []
    spread = 0.0
    T = fsun.shape[0]
    for x in (sad, sai):
        hi = np.full((T, ncell), np.nan); lo = np.full((T, ncell), np.nan)
        for t in range(T):
            np.fmax.at(hi[t], cell, x[t]); np.fmin.at(lo[t], cell, x[t])
        with np.errstate(invalid="ignore"):
            d = np.abs(hi - lo) / np.maximum(np.abs(hi), 1.0)          # W m-2: absolute below 1 W m-2
        if np.isfinite(d).any():
            spread = max(spread, float(np.nanmax(d)))
        out.append(hi)
    return out[0], out[1], spread


def components(d, ivt, k):
    """Gamma components per driver-group combination. d = (CTRL drivers, LCC drivers), each a dict of (time, pair)
    arrays: the PREV fields already shifted to step t-1, plus 'solad', 'solai' (cell light mapped to the patch)."""
    gL = {(la, cl): gamma_L(d[cl]["FSUN240"], d[la]["ELAI"]) for la in (0, 1) for cl in (0, 1)}
    gA = {la: gamma_A(ivt, d[la]["LAI240"], d[la]["ELAI"], k) for la in (0, 1)}
    gT = {lt: gamma_T(d[lt]["TV240"], d[lt]["TV24"], d[lt]["TV"], k) for lt in (0, 1)}
    gP = {}
    for cl in (0, 1):
        c = d[cl]
        for il in (0, 1):
            i = d[il]
            par_sun = (i["solad"] + c["FSUN"] * i["solai"]) * 4.6
            par24_sun = (i["FSD24"] + c["FSUN24"] * i["FSI24"]) * 4.6
            par240_sun = (i["FSD240"] + c["FSUN240"] * i["FSI240"]) * 4.6
            par_sha = (1 - c["FSUN"]) * i["solai"] * 4.6
            par240_sha = (1 - c["FSUN240"]) * i["FSI240"] * 4.6
            gP[(cl, il)] = gamma_P(par_sun, par24_sun, par240_sun, par_sha, par240_sha,
                                   c["FSUN"], c["FSUN240"], i["FSD240"], i["FSI240"], k)
    return gL, gA, gT, gP


def G_of(comp, la, cl, lt, il):
    gL, gA, gT, gP = comp
    return gL[(la, cl)] * gA[la] * gP[(cl, il)] * gT[lt]


def shapley(comp):
    """Shapley values of G over the 4 and the 3 driver groups: arrays (4, t, p) and (3, t, p); plus G_ctrl, G_lcc."""
    G = {m: G_of(comp, (m >> 0) & 1, (m >> 1) & 1, (m >> 2) & 1, (m >> 3) & 1) for m in range(16)}
    phi4 = []
    for g in range(4):
        s = 0.0
        for m in range(16):
            if not (m >> g) & 1:
                s = s + W4[bin(m).count("1")] * (G[m | (1 << g)] - G[m])
        phi4.append(s)
    # 3-group game: bit 0 = canopy (leaf_area and canopy_light together), bit 1 = leaf_temperature, bit 2 = incoming
    G3 = {m: G[(m & 1) | ((m & 1) << 1) | (((m >> 1) & 1) << 2) | (((m >> 2) & 1) << 3)] for m in range(8)}
    phi3 = []
    for g in range(3):
        s = 0.0
        for m in range(8):
            if not (m >> g) & 1:
                s = s + W3[bin(m).count("1")] * (G3[m | (1 << g)] - G3[m])
        phi3.append(s)
    return np.stack(phi4), np.stack(phi3), G[0], G[15]


def split(E0, E1, pres0, pres1, valid0, valid1, w0, w1, eps0, eps1, gc0, gc1, comp, flag):
    """Terms (TERMS4, t, p) and (TERMS3, t, p) of E1 - E0 for one compound; flag (t, p) = steps not replayable.
    Returns t4, t3, the replayed G of both runs (for validation) and the mask of flagged split steps."""
    dE = E1 - E0
    T, P = dE.shape
    t4 = np.zeros((len(TERMS4), T, P)); t3 = np.zeros((len(TERMS3), T, P))
    one = pres0 ^ pres1
    both = pres0 & pres1
    safe = both & ~(valid0 & valid1)
    ok = both & valid0 & valid1
    for t in (t4, t3):
        t[0] = np.where(one, dE, 0.0)
        t[-2] = np.where(safe, dE, 0.0)
    phi4, phi3, G0, G1 = shapley(comp)
    with np.errstate(invalid="ignore", over="ignore"):
        a0, a1 = K_UNITS * eps0 * gc0, K_UNITS * eps1 * gc1
        M0, M1 = a0 * G0, a1 * G1
        wb, Gb, ab = (w0 + w1) / 2, (G0 + G1) / 2, (a0 + a1) / 2
        plant = (M0 + M1) / 2 * (w1 - w0)[None, :]
        co2 = wb * Gb * K_UNITS * (eps0 + eps1) / 2 * (gc1 - gc0)
        ef = wb * Gb * K_UNITS * (gc0 + gc1) / 2 * (eps1 - eps0)
        g4, g3 = wb * ab * phi4, wb * ab * phi3
        parts4 = np.concatenate([plant[None], g4, co2[None], ef[None]])
        parts3 = np.concatenate([plant[None], g3, co2[None], ef[None]])
    bad = ok & (flag | ~np.isfinite(parts4).all(axis=0) | ~np.isfinite(parts3).all(axis=0))
    use = ok & ~bad
    for t, parts in ((t4, parts4), (t3, parts3)):
        n = parts.shape[0]
        t[:n] += np.where(use, parts, 0.0)
        t[-1] = dE - t[:-1].sum(axis=0)          # replay_residual: exact closure by construction
    return t4, t3, G0, G1, ok, bad
