"""Offline replay of CLM's MEGAN activity factors (option 1b, analysis/MEGAN_ATTRIBUTION.md).

Python copies of get_gamma_L, get_gamma_A, get_gamma_T, get_gamma_P in model/SourceMods/src.clm/VOCEmissionMod.F90
(same branches, same constants; class constants from megan21_emis_factors_78pft_c20161108.nc, read as float32 like
CLM reads them into r8). Inputs are the patch-level driver fields of the branch runs. gamma_C (isoprene) is not
replayed: leaf-internal CO2 is not on the tape, so CLM's GAMMAC_isoprene is used as is. gamma_SM = 1 (as in CLM).

Timing (found on the 5-day test, 2026-11-02): CLM updates ELAI and the running means (LAI240, TV24, TV240, FSUN24,
FSUN240, FSD/FSI 24/240) AFTER VOCEmission in the same step, so the tape holds the values MEGAN uses at the NEXT
step. The replay of step t therefore takes ELAI, LAI240, TV24, TV240 from step t-1 and TV, FSUN, PAR_* from step t.
The PAR_* fields (SourceMod) are written only where the isoprene gamma is valid; elsewhere (crop/grass patches with
NaN isoprene gamma) they are stale and gamma_P cannot be replayed: `fresh` marks the usable patch-steps.

Validation: python megan_replay.py HIST_FILE [HIST_FILE ...]  ->  max relative difference to CLM's GAMMA* per factor
and compound, over patch-steps where CLM wrote valid values (MEG > 0).
"""
import sys
import numpy as np
import netCDF4 as nc

FACTORS_FILE = '/cluster/shared/noresm/inputdata/atm/cam/chem/trop_mozart/emis/megan21_emis_factors_78pft_c20161108.nc'
COMPOUNDS = ['isoprene', 'pinene_a', 'carene_3', 'pinene_b', 'myrcene', 'limonene', 'ocimene_t_b', 'sabinene']
NDLLF_DCD_BRL_TREE, NBRDLF_DCD_TRP_TREE = 3, 6     # pftconMod: non-evergreen = ivt == 3 or ivt >= 6
DRIVERS = ['ELAI', 'LAI240', 'FSUN', 'FSUN24', 'FSUN240', 'FSD24', 'FSD240', 'FSI24', 'FSI240', 'TV', 'TV24', 'TV240',
           'PAR_sun', 'PAR24_sun', 'PAR240_sun', 'PAR_shade', 'PAR24_shade', 'PAR240_shade']


def class_constants():
    """{compound: dict of class constants} as CLM uses them (float32 values in r8)."""
    with nc.Dataset(FACTORS_FILE) as f:
        f.set_auto_mask(False)
        names = [b''.join(x).decode().strip() for x in f['Comp_Name'][:]]
        cls = f['Class_Num'][:]
        out = {}
        for c in COMPOUNDS:
            k = int(cls[names.index(c)]) - 1
            out[c] = {v: np.float64(f[v][k]) for v in ('LDF', 'Ceo', 'betaT', 'ct1', 'ct2', 'Anew', 'Agro', 'Amat', 'Aold')}
    return out


def gamma_L(fsun240, elai):
    return np.where((fsun240 > 0) & (fsun240 < 1e30), 0.30 * elai, 0.24 * elai)


def gamma_A(ivt, elai240, elai, k):
    decid = (ivt == NDLLF_DCD_BRL_TREE) | (ivt >= NBRDLF_DCD_TRP_TREE)
    acc = (elai240 > 0) & (elai240 < 1e30)
    prev = 2 * elai240 - elai
    with np.errstate(divide='ignore', invalid='ignore'):
        down = (k['Amat'] * (1 - (prev - elai) / prev) + k['Aold'] * (prev - elai) / prev)   # prev > elai
        up = k['Anew'] * (1 - prev / elai) + k['Amat'] * (prev / elai)                      # prev < elai
    g = np.where(prev == elai, k['Amat'], np.where(prev > elai, down, up))
    return np.where(decid[None, :] & acc, g, 1.0) if np.ndim(ivt) == 1 and np.ndim(elai) == 2 else np.where(decid & acc, g, 1.0)


def gamma_T(tv240, tv24, tv, k):
    acc = (tv240 > 0) & (tv240 < 1e30)
    topt = np.where(acc, 313.0 + 0.6 * (tv240 - 297.0), 317.0)
    eopt = np.where(acc, k['Ceo'] * np.exp(0.05 * (tv24 - 297.0)) * np.exp(0.05 * (tv240 - 297.0)), 2.26)
    x = (1.0 / topt - 1.0 / tv) / 0.00831
    ldf = eopt * (k['ct2'] * np.exp(k['ct1'] * x) / (k['ct2'] - k['ct1'] * (1.0 - np.exp(k['ct2'] * x))))
    lif = np.exp(k['betaT'] * (tv - 303.15))
    return (1 - k['LDF']) * lif + k['LDF'] * ldf


def gamma_P(par_sun, par24_sun, par240_sun, par_sha, par240_sha, fsun, fsun240, solad240, solai240, k):
    acc = (fsun240 > 0) & (fsun240 < 1) & (solad240 > 0) & (solai240 > 0)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        a_sun = np.where(acc, 0.004 - 0.0005 * np.log(par240_sun), 0.001)
        c_sun = np.where(acc, 0.0468 * np.exp(0.0005 * (par24_sun - 200.0)) * par240_sun ** 0.6, 1.21)
        a_sha = np.where(acc, 0.004 - 0.0005 * np.log(par240_sha), 0.001)
        # CLM uses the CURRENT shaded PAR (par_sha, not par24_sha) in cp for the shade part: copied as is
        c_sha = np.where(acc, 0.0468 * np.exp(0.0005 * (par_sha - 50.0)) * par240_sha ** 0.6, 1.21)
        g = (fsun * c_sun * a_sun * par_sun / np.sqrt(1 + a_sun ** 2 * par_sun ** 2)
             + (1 - fsun) * c_sha * a_sha * par_sha / np.sqrt(1 + a_sha ** 2 * par_sha ** 2))
    return (1 - k['LDF']) + k['LDF'] * g


def replay(d, prev, ivt, k):
    """Replayed gammas of one compound at the steps of d; prev = the same fields one step earlier (see Timing)."""
    return {'L': gamma_L(prev['FSUN240'], prev['ELAI']),
            'A': gamma_A(ivt, prev['LAI240'], prev['ELAI'], k),
            'T': gamma_T(prev['TV240'], prev['TV24'], d['TV'], k),
            'P': gamma_P(d['PAR_sun'], d['PAR24_sun'], d['PAR240_sun'], d['PAR_shade'], d['PAR240_shade'],
                         d['FSUN'], d['FSUN240'], d['FSD240'], d['FSI240'], k)}


def read(path, names, sel=None):
    with nc.Dataset(path) as f:
        f.set_auto_mask(False)
        out = {v: (f[v][:] if sel is None else f[v][:][:, sel]).astype(float) for v in names}   # whole field, then columns
        ivt = f['pfts1d_itype_veg'][:] if sel is None else f['pfts1d_itype_veg'][sel]
    for a in out.values():
        a[np.abs(a) >= 1e35] = np.nan
    return out, ivt


def validate(paths):
    K = class_constants()
    clm_names = ['GAMMAL', 'GAMMA_isoprene'] + [f'GAMMA{x}_{c}' for c in COMPOUNDS for x in 'ATP'] + [f'MEG_{c}' for c in COMPOUNDS]
    worst = {}
    for p in paths:
        with nc.Dataset(p) as f:
            sel = np.where(f['pfts1d_itype_veg'][:] > 0)[0]
        full, ivt = read(p, DRIVERS + clm_names, sel)
        d = {v: a[1:] for v, a in full.items()}           # steps 2.. of the file; step 1 needs the previous file
        prev = {v: a[:-1] for v, a in full.items()}
        fresh = np.isfinite(d['GAMMA_isoprene'])
        for c in COMPOUNDS:
            g = replay(d, prev, ivt, K[c])
            ok = d[f'MEG_{c}'] > 0
            for x, clm in (('L', d['GAMMAL']), ('A', d[f'GAMMAA_{c}']), ('T', d[f'GAMMAT_{c}']), ('P', d[f'GAMMAP_{c}'])):
                use = ok & fresh if x == 'P' else ok
                rel = np.abs(g[x][use] / clm[use] - 1)
                rel = rel[np.isfinite(rel)]
                m = float(rel.max()) if rel.size else np.nan
                q = float(np.quantile(rel, 0.999)) if rel.size else np.nan
                w = worst.get((c, x), (0, 0, 0))
                worst[(c, x)] = (max(w[0], m), max(w[1], q), w[2] + int(use.sum()))
    print(f'{"compound":<12} {"factor":<6} {"max rel diff":>13} {"p99.9":>10} {"n":>10}')
    for (c, x), (m, q, n) in worst.items():
        print(f'{c:<12} {x:<6} {m:13.2e} {q:10.2e} {n:10d}')
    return worst


if __name__ == '__main__':
    validate(sys.argv[1:])
