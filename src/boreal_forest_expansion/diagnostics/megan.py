"""MEGAN compounds, their mapping to CAM species, and OH rate constants.

Sources
  - MEGAN_SPECIFIER: your CaseDocs/drv_flds_in (identical to the tropstratchem use-case
    default in bld/namelist_files/use_cases/*_cam6_noresm_tropstratchem.xml) (a).
  - Formulas of the MEGAN compounds: standard chemistry; molecular weight and carbon
    number are computed from them. CLM uses the molecular weights from
    megan_factors_file; these should agree (b, the file was not read).
  - OH rate constants: pp_tropstrat_mam_oslo/chem_mech.in and mo_usrrxt.F90 /
    mo_jpl.F90 of the CAM fork (branch new-case-set) (a). Line numbers in comments.

How emissions reach CAM (a, CLM VOCEmissionMod.F90 and CAM chemistry.F90):
  CLM history MEG_<compound> is kg(compound) m-2 s-1. CLM sends CAM, per CAM species,
  sum(coeff * E_compound / MW_compound) in mol m-2 s-1; CAM multiplies by the CAM
  species mass. Moles are conserved, mass is not (tricyclene, C10H16, enters BIGALK,
  a C5 species). Budgets here are therefore built in moles.
"""

from __future__ import annotations

import math
import re

MEGAN_SPECIFIER = """
'ISOP = isoprene',
'MTERP = pinene_a + carene_3 + thujene_a + 2met_styrene + cymene_p + cymene_o + terpinolene + bornene + fenchene_a + ocimene_al + pinene_b + sabinene + camphene + limonene + phellandrene_a + terpinene_g + terpinene_a + phellandrene_b +  myrcene + ocimene_t_b + ocimene_c_b',
'BCARY = caryophyllene_b + bergamotene_a + bisabolene_b + farnescene_b + humulene_a',
'CH3OH = methanol', 'C2H5OH = ethanol', 'CH2O = formaldehyde',
'CH3CHO = acetaldehyde', 'CH3COOH = acetic_acid', 'CH3COCH3 = acetone',
'HCOOH = formic_acid', 'HCN = hydrogen_cyanide', 'CO = carbon_monoxide',
'C2H6 = ethane', 'C2H4 = ethene', 'C3H8 = propane', 'C3H6 = propene',
'BIGALK = pentane + hexane + heptane + tricyclene', 'BIGENE = butene',
'TOLUENE = toluene'
"""

FORMULAS = {
    "isoprene": "C5H8",
    # monoterpenes (MTERP)
    "pinene_a": "C10H16", "carene_3": "C10H16", "thujene_a": "C10H16", "2met_styrene": "C9H10",
    "cymene_p": "C10H14", "cymene_o": "C10H14", "terpinolene": "C10H16", "bornene": "C10H16",
    "fenchene_a": "C10H16", "ocimene_al": "C10H16", "pinene_b": "C10H16", "sabinene": "C10H16",
    "camphene": "C10H16", "limonene": "C10H16", "phellandrene_a": "C10H16", "terpinene_g": "C10H16",
    "terpinene_a": "C10H16", "phellandrene_b": "C10H16", "myrcene": "C10H16", "ocimene_t_b": "C10H16",
    "ocimene_c_b": "C10H16",
    # sesquiterpenes (BCARY)
    "caryophyllene_b": "C15H24", "bergamotene_a": "C15H24", "bisabolene_b": "C15H24",
    "farnescene_b": "C15H24", "humulene_a": "C15H24",
    # oxygenated
    "methanol": "CH4O", "ethanol": "C2H6O", "formaldehyde": "CH2O", "acetaldehyde": "C2H4O",
    "acetic_acid": "C2H4O2", "acetone": "C3H6O", "formic_acid": "CH2O2",
    # others
    "hydrogen_cyanide": "HCN", "carbon_monoxide": "CO",
    "ethane": "C2H6", "ethene": "C2H4", "propane": "C3H8", "propene": "C3H6",
    "pentane": "C5H12", "hexane": "C6H14", "heptane": "C7H16", "tricyclene": "C10H16",
    "butene": "C4H8", "toluene": "C7H8",
}

ATOMIC_MASS = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007}

# Groups of CAM species used in the tables. "ISOP+MTERP" = what the fBVOC runs prescribe.
GROUPS = {
    "ISOP+MTERP (prescribed in fBVOC)": ["ISOP", "MTERP"],
    "BCARY": ["BCARY"],
    "oxygenated VOC": ["CH3OH", "C2H5OH", "CH2O", "CH3CHO", "CH3COOH", "CH3COCH3", "HCOOH"],
    "CO": ["CO"],
    "other hydrocarbons": ["C2H6", "C2H4", "C3H8", "C3H6", "BIGALK", "BIGENE", "TOLUENE"],
    "HCN": ["HCN"],
}
PRESCRIBED_GROUP = "ISOP+MTERP (prescribed in fBVOC)"

# Species that form SOA in pp_tropstrat_mam_oslo (chem_mech.in lines 1173-1178, plus DMS) (a)
SOA_PRECURSORS = {"ISOP", "MTERP"}


def parse_formula(formula: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        counts[el] = counts.get(el, 0) + (int(n) if n else 1)
    return counts


def molar_mass(formula: str) -> float:
    """g mol-1"""
    return sum(ATOMIC_MASS[el] * n for el, n in parse_formula(formula).items())


def carbon_number(formula: str) -> int:
    return parse_formula(formula).get("C", 0)


def parse_specifier(spec: str = MEGAN_SPECIFIER) -> dict[str, list[tuple[float, str]]]:
    """'MTERP = a + b' -> {'MTERP': [(1.0, 'a'), (1.0, 'b')]}. Coefficients like '0.5*x' are kept."""
    out: dict[str, list[tuple[float, str]]] = {}
    for entry in re.findall(r"'([^']+)'", spec):
        lhs, rhs = (s.strip() for s in entry.split("=", 1))
        terms = []
        for t in rhs.split("+"):
            t = t.strip()
            if "*" in t:
                c, name = t.split("*", 1)
                terms.append((float(c), name.strip()))
            else:
                terms.append((1.0, t))
        out[lhs] = terms
    return out


def compound_table(spec: str = MEGAN_SPECIFIER) -> list[dict]:
    """One row per MEGAN compound: CAM species, coefficient, MW, carbon number."""
    rows = []
    for cam, terms in parse_specifier(spec).items():
        for coeff, name in terms:
            if name not in FORMULAS:
                raise KeyError(f"No formula for MEGAN compound '{name}'; add it to FORMULAS")
            f = FORMULAS[name]
            rows.append({"compound": name, "cam_species": cam, "coeff": coeff, "formula": f,
                         "mw": molar_mass(f), "nC": carbon_number(f)})
    return rows


def group_of(cam_species: str) -> str:
    for g, members in GROUPS.items():
        if cam_species in members:
            return g
    return "unassigned"


# --- OH rate constants (cm3 molecule-1 s-1) ------------------------------------------

K_BOLTZ = 1.380649e-23


def air_number_density(T: float, p_pa: float) -> float:
    """molecules cm-3"""
    return p_pa / (K_BOLTZ * T) * 1e-6


def _arr(A, B=0.0):
    return lambda T, M: A * math.exp(B / T)


def _troe(ko0, no, kinf0, ninf, fc):
    """Termolecular (+M) form as in mo_jpl.F90; the rate is multiplied by M because the
    reaction carries '+ M' in chem_mech.in (b, standard MOZART preprocessor convention)."""
    def k(T, M):
        ko = ko0 * (300.0 / T) ** no
        kinf = kinf0 * (300.0 / T) ** ninf
        x = ko * M / kinf
        return M * ko / (1 + x) * fc ** (1.0 / (1.0 + math.log10(x) ** 2))
    return k


def _co_oh(T, M):
    """CO + OH: CO_OH_M (troe, line 873) + usr_CO_OH_b (mo_usrrxt.F90)."""
    k1 = _troe(5.9e-33, 1.0, 1.1e-12, -1.3, 0.6)(T, M)
    kinf = 2.1e9 * (T / 300.0) ** 6.1
    ko = 1.5e-13
    x = ko * M / kinf
    k2 = ko / (1 + x) * 0.6 ** (1.0 / (1.0 + math.log10(x) ** 2))
    return k1 + k2


K_OH = {  # chem_mech.in line numbers in pp_tropstrat_mam_oslo
    "ISOP": _arr(2.54e-11, 410),            # 1006
    "MTERP": _arr(1.2e-11, 440),            # 1070
    "BCARY": _arr(2e-10),                   # 1067
    "CH3OH": _arr(2.9e-12, -345),           # 870
    "C2H5OH": _arr(6.9e-12, -230),          # 895
    "CH2O": _arr(5.5e-12, 125),             # 865
    "CH3CHO": _arr(4.63e-12, 350),          # 900
    "CH3COOH": _arr(7e-13),                 # 906
    "CH3COCH3": lambda T, M: 3.82e-11 * math.exp(-2000 / T) + 1.33e-13,   # usr_CH3COCH3_OH
    "HCOOH": _arr(4e-13),                   # 875
    "HCN": _troe(4.28e-33, 0.0, 9.3e-15, -4.42, 0.8),   # 874
    "CO": _co_oh,                           # 873 + usr_CO_OH_b
    "C2H6": _arr(7.66e-12, -1020),          # 898
    "C2H4": _troe(8.6e-29, 3.1, 9e-12, 0.85, 0.48),     # 915
    "C3H8": _arr(8.7e-12, -615),            # 927
    "C3H6": _troe(8e-27, 3.5, 3e-11, 0.0, 0.5),         # 939
    "BIGALK": _arr(3.5e-12),                # 981
    "BIGENE": _arr(5.4e-11),                # 945
    "TOLUENE": _arr(1.7e-12, 352),          # 1052
}


def k_oh(species: str, T: float = 298.0, p_pa: float = 101325.0) -> float:
    return K_OH[species](T, air_number_density(T, p_pa))
