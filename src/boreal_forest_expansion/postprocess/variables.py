"""Which NorESM2.3 history variables to keep, grouped by component and category.

Names follow the NorESM2.3 output (CAM cam_noresm2_3_v1.0.0j + OsloAero oslo_aero_2_3a5,
CLM release-clm5.0.14-Nor_v1.0.7). Selection is presence-based: a variable listed here
but missing from the history files is reported and skipped, never a crash.

Each processed file = ALWAYS_INCLUDE[component] + the variables of one category
(+ the secondary variables that `derived.py` assigns to that category).

Changes vs the old code (old: postprocess.variables_by_component + atm/lnd_always_include)
--------------------------------------------------------------------------------------
- RENAMED  SFisoprene -> SFISOP, SFmonoterp -> SFMTERP (tropstratchem names); added SFBCARY.
- REMOVED  GRIDAREA (not in NorESM2.3 output; use gw), CLOUDCOVER_CLUBB (not in output),
           cb_SOA_A1/NA and *_OCW (not in output; computed instead as SOA_A1_cb etc.,
           see derived.py).
- REMOVED  T, TS, U, V from always-include (moved to METEO): a missing 3D field no
           longer breaks every category.
- REMOVED  the casename 'OFF' test for BVOC runs: selection is now by presence in the file.
- ADDED    CAM: all remaining fields of the curated fincl list, in new categories
           SULFATE, AEROPT, CHEM (O3, OH, CH4, tropopause), METEO. Only emis_ISOP and
           emis_MTERP are not kept (exact duplicates of SFISOP/SFMTERP, see BVOC below).
- ADDED    CLM: targeted subset of the ~560 default fields: ENERGY (incl. vis/NIR,
           direct/diffuse, sensible heat split vegetation/ground), SNOW (incl. canopy snow
           and snow-reflected solar), daily min/max 2 m temperature, more carbon pools, QA
           (conservation errors), and all 46 MEGAN compounds that CAM uses: the 27 lumped
           into ISOP/MTERP/BCARY (old list had 7 of 21 monoterpenes) plus the 19
           non-terpene compounds that feed CAM gas-phase chemistry; MEGAN activity factors.
- MOVED    LHFLX, SHFLX from RADIATIVE to METEO.
- FIXED    N_AER units label: "unitless" in the file, really cm-3 (UNIT_LABEL_FIXES).
"""

# Grid, weights and vertical coordinate: written into every processed file.
ALWAYS_INCLUDE = {
    "atm": [
        "gw",                     # latitude weights (use for area means; GRIDAREA no longer exists)
        "LANDFRAC",
        "P0", "PS", "hyai", "hybi", "hyam", "hybm",   # needed to rebuild layer pressures/thicknesses
    ],
    "lnd": [
        "area",                   # grid-cell area [km^2]; land area = area * landfrac
        "landfrac", "landmask", "pftmask",
        "PCT_LANDUNIT",
    ],
}

# MEGAN compound lumping for the trop_strat chemistry (CAM bld/build-namelist default).
# Check your run: grep -A6 megan_specifier CaseDocs/drv_flds_in
MEGAN_LUMPING = {
    "ISOP": ["isoprene"],
    "MTERP": ["pinene_a", "carene_3", "thujene_a", "2met_styrene", "cymene_p", "cymene_o",
              "terpinolene", "bornene", "fenchene_a", "ocimene_al", "pinene_b", "sabinene",
              "camphene", "limonene", "phellandrene_a", "terpinene_g", "terpinene_a",
              "phellandrene_b", "myrcene", "ocimene_t_b", "ocimene_c_b"],
    "BCARY": ["caryophyllene_b", "bergamotene_a", "bisabolene_b", "farnescene_b", "humulene_a"],
    # Non-terpene compounds: feed CAM gas-phase chemistry (ozone, OH -> methane lifetime).
    "CH3OH": ["methanol"], "C2H5OH": ["ethanol"], "CH2O": ["formaldehyde"],
    "CH3CHO": ["acetaldehyde"], "CH3COOH": ["acetic_acid"], "CH3COCH3": ["acetone"],
    "HCOOH": ["formic_acid"], "HCN": ["hydrogen_cyanide"], "CO": ["carbon_monoxide"],
    "C2H6": ["ethane"], "C2H4": ["ethene"], "C3H8": ["propane"], "C3H6": ["propene"],
    "BIGALK": ["pentane", "hexane", "heptane", "tricyclene"], "BIGENE": ["butene"],
    "TOLUENE": ["toluene"],
}
# Compounds for which CLM writes MEGAN emission factors (EPS_) and activity factors (GAMMA*_)
_MEGAN_FACTOR_COMPOUNDS = ["isoprene", "pinene_a", "pinene_b", "carene_3", "sabinene",
                           "limonene", "myrcene", "ocimene_t_b", "methanol", "acetone"]

CATEGORIES = {
    # CAM: the h0 list is a curated fincl, so every field is kept (except two duplicates).
    "atm": {
        # Emitted BVOC and their gas-phase burdens. SF* = everything the atmosphere receives
        # (MEGAN + prescribed files); MEG_* = the interactive MEGAN part only.
        # emis_ISOP/emis_MTERP are NOT listed: in OsloAero src_cam/chemistry.F90 (chem_emissions)
        # SF<X> and emis_<X> are written by consecutive outfld calls on the same array
        # cam_in%cflx(:ncol,m), so they are identical.
        "BVOC": [
            "SFISOP", "SFMTERP", "SFBCARY",
            "MEG_ISOP", "MEG_MTERP", "MEG_BCARY",
            "ISOP", "MTERP", "BCARY",
            "cb_ISOP", "cb_MTERP", "cb_BCARY",
        ],
        # Secondary organic aerosol: concentrations, NPF, growth, budget terms, CCN.
        "SOA": [
            "SOA_A1", "SOA_NA", "SOA_LV", "SOA_SV", "cb_SOA_LV", "cb_SOA_SV",
            "NUCLRATE", "FORMRATE", "GR", "GRSOA", "GRH2SO4",
            "NUCLSOA", "ORGNUCL", "COAGNUCL",
            "SOA_A1condTend", "SOA_NAcondTend", "SOA_A1coagTend", "SOA_NAcoagTend",
            "SOA_A1_mixnuc1", "SOA_NA_mixnuc1",
            "SOA_A1DDF", "SOA_NADDF", "SOA_A1SFWET", "SOA_NASFWET",
            "N_AER",
            "CCN1", "CCN2", "CCN3", "CCN4", "CCN5", "CCN6", "CCN7", "CCN_B",
        ],
        # Sulfate and H2SO4: the co-nucleating and coating partner of SOA.
        "SULFATE": [
            "H2SO4", "cb_H2SO4", "DF_H2SO4", "WD_H2SO4", "WD_A_H2SO4",
            "SO4_A1", "SO4_NA",
            "SO4_A1condTend", "SO4_NAcondTend", "SO4_A1coagTend", "SO4_NAcoagTend",
            "SO4_A1_mixnuc1", "SO4_NA_mixnuc1",
            "SO4_A1DDF", "SO4_NADDF", "SO4_A1SFWET", "SO4_NASFWET",
        ],
        # Aerosol optical properties (direct effect).
        "AEROPT": [
            "DOD440", "DOD550", "DOD870", "AOD_VIS", "AEROD_v", "OD550DRY",
            "ABS550", "AB550DRY", "CABS550", "ABS550_A",
            "A550_BC", "A550_DU", "A550_POM", "A550_SO4", "A550_SS",
        ],
        # Cloud microphysics. NOTE: AREL, AWNC, ACTREL, ACTNL (and the ice analogues AREI,
        # ACTREI) are written as (value x cloud fraction). Use derived.incloud().
        "CLOUDPROP": [
            "AREL", "AWNC", "FREQL", "ACTREL", "ACTNL", "FCTL",
            "AREI", "FREQI", "ACTREI", "FCTI",
            "CDNUMC", "CLDLIQ", "NUMLIQ", "CLDICE", "NUMICE", "CLOUD",
            "CLDTOT", "CLDLOW", "CLDMED", "CLDHGH",
            "TGCLDLWP", "TGCLDIWP", "TGCLDCWP",
        ],
        # Radiative fluxes: Ghan inputs, standard CRE, TOA vs top-of-model, surface.
        "RADIATIVE": [
            "FSNT", "FLNT", "FSNT_DRF", "FLNT_DRF", "FSNTCDRF", "FLNTCDRF",
            "FSNTC", "FLNTC", "SWCF", "LWCF",
            "FSNTOA", "FSNTOAC", "FLUT", "FLUTC", "SOLIN",
            "FSDS", "FSDSC", "FSNS", "FSNSC", "FLDS", "FLNS", "FLNSC", "FLUS",
            "FSDS_DRF", "FSDSCDRF", "FSUS_DRF", "FSUTADRF",
        ],
        # Oxidants and trace gases: ozone and methane-lifetime channels.
        "CHEM": [
            "O3", "OH", "HO2", "NO", "NO2", "CO", "CH4",
            "TROP_P", "TROP_T", "TROP_Z",
        ],
        # Meteorology, surface state and turbulent fluxes.
        "METEO": [
            "TS", "TREFHT", "QREFHT", "U10", "PSL",
            "LHFLX", "SHFLX", "TAUX", "TAUY",
            "PRECC", "PRECL", "PRECSC", "PRECSL",
            "SNOWHLND", "ICEFRAC", "OCNFRAC",
            "T", "U", "V", "Q", "OMEGA", "Z3",
        ],
    },
    # CLM: the h0 list is the CLM default (~560 fields), so only a targeted subset is kept.
    "lnd": {
        # Surface state and vegetation structure.
        "LAND": [
            "TSA", "TREFMNAV", "TREFMXAV",          # 2 m mean, daily min, daily max
            "Q2M", "RH2M", "TG", "TV", "TSKIN", "TSOI_10CM", "SOILWATER_10CM", "ALT",
            "PCT_NAT_PFT", "TLAI", "ELAI", "TSAI", "ESAI", "HTOP", "LAISUN", "LAISHA",
        ],
        # Surface energy balance. Broadband albedo = FSR / FSDS; by band and beam:
        # vis direct = FSRVD / FSDSVD, vis diffuse = FSRVI / FSDSVI, NIR = FSRND/FSDSND, ...
        "ENERGY": [
            "FSDS", "FSR", "FSA", "SABG", "SABV", "FLDS", "FIRA", "FIRE",
            "FSH", "FSH_V", "FSH_G",                # sensible heat: total, vegetation, ground
            "EFLX_LH_TOT", "FGR",
            "FSDSVD", "FSDSVI", "FSDSND", "FSDSNI", "FSRVD", "FSRVI", "FSRND", "FSRNI",
        ],
        # Snow: the canopy-masking part of the boreal albedo signal.
        # SNOCAN = snow held in the canopy; SNOFSR* = solar reflected by snow (vis/NIR,
        # direct/diffuse). SNOWDP = gridcell-mean snow height, SNOW_DEPTH = over snow-covered area.
        "SNOW": [
            "H2OSNO", "FSNO", "FSNO_EFF", "SNOW_DEPTH", "SNOWDP", "SNOW_PERSISTENCE",
            "SNOCAN", "SNOFSRVD", "SNOFSRVI", "SNOFSRND", "SNOFSRNI",
        ],
        "BIOGEOCHEM": [
            "GPP", "NPP", "AR", "HR", "ER", "NEE", "NEP", "NBP",
            "LEAFC", "WOODC", "TOTVEGC", "TOTPFTC", "TOTLITC", "TOTSOMC",
            "TOTCOLC", "TOTECOSYSC", "STORVEGC",
            "TOTVEGN", "TOTPFTN", "STORVEGN",
        ],
        # Speciated MEGAN fluxes for every compound in MEGAN_LUMPING (all 46 that CAM
        # receives: terpenes for SOA, the rest for gas-phase chemistry),
        # plus MEGAN factors to attribute emission changes:
        #   EPS_ (emission factor: PFT composition), GAMMAL (LAI), GAMMAT_ (temperature),
        #   GAMMAP_ (light), GAMMAA_ (leaf age), GAMMA_ (total activity).
        "BVOC": (
            [f"MEG_{c}" for species in MEGAN_LUMPING.values() for c in species]
            + ["GAMMAL", "GAMMAS", "GAMMAC_isoprene"]
            + [f"{p}_{c}" for c in _MEGAN_FACTOR_COMPOUNDS
               for p in ("EPS", "GAMMA", "GAMMAT", "GAMMAP", "GAMMAA")]
        ),
        # Evapotranspiration components. Vegetation ET = QVEGE + QVEGT.
        "ET": ["QFLX_EVAP_TOT", "QSOIL", "QVEGE", "QVEGT", "FCEV", "FCTR", "FGEV"],
        # Conservation errors: a one-off check that the modified surface data behaves.
        # All should be ~0 everywhere (energy in W/m2, water in mm).
        "QA": ["ERRSEB", "ERRSOL", "ERRSOI", "ERRH2O", "ERRH2OSNO"],
    },
}

# Metadata corrections (no numeric change). Verified in the source code:
# N_AER is summed from mode concentrations after a x1e-6 conversion to #/cm3
# (oslo_aero_optical_params.F90), but is registered with units "unitless".
UNIT_LABEL_FIXES = {
    "atm": {"N_AER": "cm-3"},
    "lnd": {},
}


def variables_for(component, categories=None):
    """Return the flat list of variables to read for `component` and `categories`."""
    _check_component(component)
    cats = categories or list(CATEGORIES[component])
    unknown = [c for c in cats if c not in CATEGORIES[component]]
    if unknown:
        raise ValueError(f"Unknown {component} categories {unknown}; "
                         f"choose from {list(CATEGORIES[component])}")
    names = list(ALWAYS_INCLUDE[component])
    for cat in cats:
        names += [v for v in CATEGORIES[component][cat] if v not in names]
    return names


def _check_component(component):
    if component not in CATEGORIES:
        raise ValueError(f"component must be one of {list(CATEGORIES)}, got {component!r}")
