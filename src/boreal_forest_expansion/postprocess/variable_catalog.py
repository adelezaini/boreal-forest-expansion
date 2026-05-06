# src/boreal_forest_expansion/postprocess/variable_catalog.py

"""
Variable catalog for postprocessed CAM diagnostics.

These classes are used by postprocess/postprocess.py to save files as:

    [casealias]_[variableclass]_[startyr]_[endyr].nc

Example:
    CTRL_BVOC_2000_2009.nc
    LCC-PD_CH4_2000_2009.nc

The catalog includes both native CAM variables and derived variables created by:
- transform.py
- ghan_decomposition.py
- chemistry_postprocess.py
"""

VARIABLE_CLASSES = {
    # -------------------------------------------------------------------------
    # Core CH4 burden, loss, lifetime diagnostics
    # -------------------------------------------------------------------------
    "CH4": [
        "CH4",
        "CH4_SRF",
        "SFCH4",
        "CH4_burden_kg",
        "CH4_burden_Tg",
        "CH4_burden_trop_kg",
        "CH4_burden_trop_Tg",
        "CH4_OH_loss_kg_s",
        "CH4_OH_loss_Tg_yr",
        "CH4_lifetime_OH_yr",
        "CH4_SRF_global_mean",
    ],

    # -------------------------------------------------------------------------
    # BVOC emissions, BVOC tracers, and BVOC oxidation products
    # -------------------------------------------------------------------------
    "BVOC": [
        # MEGAN emissions
        "MEG_ISOP",
        "MEG_MTERP",
        "MEG_CH2O",
        "MEG_CH3CHO",
        "MEG_CH3COCH3",
        "MEG_CH3OH",
        "MEG_CO",
        "MEG_C2H4",
        "MEG_C2H5OH",
        "MEG_C2H6",
        "MEG_C3H6",
        "MEG_C3H8",

        # Total surface fluxes / emissions
        "SFISOP",
        "SFMTERP",
        "SFCH2O",
        "SFCH3CHO",
        "SFCH3COCH3",
        "SFCH3OH",
        "SFCO",
        "SFC2H4",
        "SFC3H6",
        "SFBIGALK",
        "SFBIGENE",
        "SFTOLUENE",
        "SFXYLENES",
        "emis_ISOP",
        "emis_MTERP",

        # Derived global emissions
        "MEG_ISOP_Tg_yr",
        "MEG_MTERP_Tg_yr",
        "SFISOP_Tg_yr",
        "SFMTERP_Tg_yr",
        "emis_ISOP_Tg_yr",
        "emis_MTERP_Tg_yr",

        # BVOC tracers
        "ISOP",
        "ISOP_SRF",
        "MTERP",
        "MTERP_SRF",
        "BIGALK",
        "BIGALK_SRF",
        "BIGENE",
        "BIGENE_SRF",
        "BENZENE",
        "BENZENE_SRF",
        "TOLUENE",
        "TOLUENE_SRF",
        "XYLENES",
        "XYLENES_SRF",

        # BVOC oxidation products / organic nitrates
        "CH2O",
        "CH2O_SRF",
        "CH3COCH3",
        "CH3COCH3_SRF",
        "CH3OH",
        "CH3OH_SRF",
        "MACR",
        "MACR_SRF",
        "MVK",
        "MVK_SRF",
        "IEPOX",
        "IEPOX_SRF",
        "ISOPOOH",
        "ISOPOOH_SRF",
        "ISOPNO3",
        "ISOPNO3_SRF",
        "ONITR",
        "ONITR_SRF",
        "TERPNIT",
        "TERPNIT_SRF",
        "TERPROD1",
        "TERPROD1_SRF",
        "TERPROD2",
        "TERPROD2_SRF",
        "MPAN",
        "MPAN_SRF",

        # Derived means
        "ISOP_trop_massmean",
        "MTERP_trop_massmean",
        "CH2O_trop_massmean",
    ],

    # -------------------------------------------------------------------------
    # Ozone diagnostics
    # -------------------------------------------------------------------------
    "OZONE": [
        "O3",
        "O3_SRF",
        "DF_O3",
        "O3_burden_kg",
        "O3_burden_Tg",
        "O3_trop_massmean",
        "O3_SRF_global_mean",
    ],

    # -------------------------------------------------------------------------
    # Oxidation capacity and gas-phase chemistry context
    # -------------------------------------------------------------------------
    "CHEMISTRY": [
        # HOx
        "OH",
        "OH_SRF",
        "HO2",
        "HO2_SRF",
        "H2O2",
        "H2O2_SRF",

        # CO / CO2 / methane-adjacent gases
        "CO",
        "CO_SRF",
        "CO2",
        "CO2_SRF",
        "N2O",
        "N2O_SRF",

        # NOx / NOy
        "NO",
        "NO_SRF",
        "NO2",
        "NO2_SRF",
        "NO3",
        "NO3_SRF",
        "N2O5",
        "HNO3",
        "HNO3_SRF",
        "PAN",
        "PAN_SRF",
        "NOx",

        # Sulfur / ammonia chemistry
        "SO2",
        "SO2_SRF",
        "H2SO4",
        "H2SO4_SRF",
        "DMS",
        "DMS_SRF",
        "NH3",
        "NH3_SRF",

        # Chemistry tendencies / rates / deposition
        "FORMRATE",
        "DF_H2SO4",
        "DF_HNO3",
        "DF_NH3",
        "DF_SO2",
        "WD_H2SO4",
        "WD_HNO3",
        "WD_A_H2SO4",
        "WD_A_HNO3",
        "WD_A_NH3",
        "WD_A_SO2",
        "WD_A_ISOP",
        "WD_A_MTERP",

        # Derived mass-weighted chemistry means
        "OH_trop_massmean",
        "HO2_trop_massmean",
        "H2O2_trop_massmean",
        "CO_trop_massmean",
        "NO_trop_massmean",
        "NO2_trop_massmean",
        "NOx_trop_massmean",
        "NO3_trop_massmean",
        "HNO3_trop_massmean",
        "PAN_trop_massmean",
    ],

    # -------------------------------------------------------------------------
    # Aerosol mass, number, burdens, deposition, and optical depth
    # -------------------------------------------------------------------------
    "AEROSOL": [
        # Aerosol optical depth / extinction / absorption
        "AEROD_v",
        "AOD_VIS",
        "ABS550",
        "ABSVIS",
        "AB550DRY",
        "BS550AER",
        "CABS550",
        "CABS550A",
        "CAODVIS",
        "A550_BC",
        "A550_DU",
        "A550_POM",
        "A550_SO4",
        "A550_SS",
        "D550_BC",
        "D550_DU",
        "D550_POM",
        "D550_SO4",
        "D550_SS",
        "EC550AER",
        "EC550BC",
        "EC550DU",
        "EC550POM",
        "EC550SO4",
        "EC550SS",
        "CDOD440",
        "CDOD550",
        "CDOD870",
        "DOD550",

        # Aerosol species / modes
        "BC_A",
        "BC_AC",
        "BC_AI",
        "BC_N",
        "BC_NI",
        "OM_AC",
        "OM_AI",
        "OM_NI",
        "DST_A2",
        "DST_A3",
        "SS_A1",
        "SS_A2",
        "SS_A3",

        # Aerosol burdens
        "cb_BC",
        "cb_DUST",
        "cb_H2SO4",
        "cb_OM",
        "cb_SALT",
        "cb_SO4_NA",
        "cb_SULFATE",
        "DLOAD_BC",
        "DLOAD_MI",
        "DLOAD_OC",
        "DLOAD_S4",
        "DLOAD_SS",

        # Aerosol mass mixing ratios
        "mmr_BC",
        "mmr_DUST",
        "mmr_OM",
        "mmr_SALT",
        "mmr_SULFATE",

        # Aerosol emissions / deposition
        "emis_BC",
        "emis_DMS",
        "emis_DUST",
        "emis_OM",
        "emis_SALT",
        "emis_SO2",
        "dry_BC",
        "dry_DUST",
        "dry_OM",
        "dry_SALT",
        "dry_SULFATE",
        "wet_BC",
        "wet_DUST",
        "wet_OM",
        "wet_SALT",
        "wet_SO2",
        "wet_SULFATE",
        "wet_SULFATESOA_A1DDF",

        # CCN and aerosol microphysics
        "CCN1",
        "CCN2",
        "CCN3",
        "CCN4",
        "CCN5",
        "CCN6",
        "CCN7",
        "CCN_B",
        "NCONC01",
        "NCONC02",
        "NCONC03",
        "NCONC04",
        "NCONC05",
        "NCONC06",
        "NCONC07",
        "NCONC08",
        "NCONC09",
        "NCONC10",
        "NCONC11",
        "NCONC12",
        "NCONC13",
        "NCONC14",
        "NMR01",
        "NMR02",
        "NMR03",
        "NMR04",
        "NMR05",
        "NMR06",
        "NMR07",
        "NMR08",
        "NMR09",
        "NMR10",
        "NMR11",
        "NMR12",
        "NMR13",
        "NMR14",
        "SIGMA01",
        "SIGMA02",
        "SIGMA03",
        "SIGMA04",
        "SIGMA05",
        "SIGMA06",
        "SIGMA07",
        "SIGMA08",
        "SIGMA09",
        "SIGMA10",
        "SIGMA11",
        "SIGMA12",
        "SIGMA13",
        "SIGMA14",
        "HYGRO01",
        "HYGRO02",
        "HYGRO03",
        "HYGRO04",
        "HYGRO05",
        "HYGRO06",
        "HYGRO07",
        "HYGRO08",
        "HYGRO09",
        "HYGRO10",
        "HYGRO11",
        "HYGRO12",
        "HYGRO13",
        "HYGRO14",
        "COAGNUCL",
        "NUCLRATE",
        "NUCLSOA",
        "ORGNUCL",
        "GR",
        "GRH2SO4",
        "GRSOA",
        "NNAT_0",
    ],

    # -------------------------------------------------------------------------
    # Secondary organic aerosol and sulfate-process diagnostics
    # -------------------------------------------------------------------------
    "SOA": [
        # SOA tracers
        "SOA_A1",
        "SOA_NA",
        "SOA_LV",
        "SOA_SV",
        "SOA_A1_ugkg",
        "SOA_NA_ugkg",

        # SOA burdens
        "cb_SOA_LV",
        "cb_SOA_NA",
        "cb_SOA_SV",
        "cb_SOA_NA_mgm2",
        "cb_SOA_dry",

        # SOA tendencies / sinks
        "SOA_A1DDF",
        "SOA_A1GVF",
        "SOA_A1SFWET",
        "SOA_A1TBF",
        "SOA_A1_OCWDDF",
        "SOA_A1_OCWSFWET",
        "SOA_A1_OCW_mixnuc1",
        "SOA_A1_OCWclcoagTend",
        "SOA_A1_mixnuc1",
        "SOA_A1coagTend",
        "SOA_A1condTend",
        "SOA_NADDF",
        "SOA_NAGVF",
        "SOA_NASFWET",
        "SOA_NATBF",
        "SOA_NA_OCWDDF",
        "SOA_NA_OCWSFWET",
        "SOA_NA_OCW_mixnuc1",
        "SOA_NA_mixnuc1",
        "SOA_NAclcoagTend",
        "SOA_NAcoagTend",
        "SOA_NAcondTend",

        # Sulfate process diagnostics useful for SOA/sulfate interactions
        "SO4_A1",
        "SO4_A2",
        "SO4_AC",
        "SO4_NA",
        "SO4_PR",
        "SO4_A1DDF",
        "SO4_A1GVF",
        "SO4_A1SFWET",
        "SO4_A1TBF",
        "SO4_A1_OCWDDF",
        "SO4_A1_OCWSFWET",
        "SO4_A1_OCW_mixnuc1",
        "SO4_A1_mixnuc1",
        "SO4_A1clcoagTend",
        "SO4_A1coagTend",
        "SO4_A1condTend",
        "SO4_A2DDF",
        "SO4_A2GVF",
        "SO4_A2SFWET",
        "SO4_A2TBF",
        "SO4_A2_OCW_mixnuc1",
        "SO4_A2_OCWclcoagTend",
        "SO4_A2_mixnuc1",
        "SO4_ACDDF",
        "SO4_ACGVF",
        "SO4_ACSFWET",
        "SO4_ACTBF",
        "SO4_AC_OCW_mixnuc1",
        "SO4_AC_mixnuc1",
        "SO4_ACcoagTend",
        "SO4_NADDF",
        "SO4_NAGVF",
        "SO4_NASFWET",
        "SO4_NATBF",
        "SO4_NA_OCWDDF",
        "SO4_NA_OCWSFWET",
        "SO4_NA_OCW_mixnuc1",
        "SO4_NA_mixnuc1",
        "SO4_NAclcoagTend",
        "SO4_NAcoagTend",
        "SO4_NAcondTend",
        "SO4_PRDDF",
        "SO4_PRGVF",
        "SO4_PRSFWET",
        "SO4_PRTBF",
        "SO4_PR_OCW_mixnuc1",
        "SO4_PR_mixnuc1",
    ],

    # -------------------------------------------------------------------------
    # Cloud properties and cloud diagnostics
    # -------------------------------------------------------------------------
    "CLOUDPROP": [
        "CLDFREE",
        "CLOUD",
        "CLDTOT",
        "CLDTOT_CAL",
        "CLDLOW",
        "CLDLOW_CAL",
        "CLDMED",
        "CLDMED_CAL",
        "CLDHGH",
        "CLDHGH_CAL",
        "CLDICE",
        "CLDLIQ",
        "CLDTOT_pct",
        "CLDLOW_pct",
        "CLDMED_pct",
        "CLDHGH_pct",
        "CLDICE_mgkg",
        "CLDLIQ_mgkg",
        "FCTI",
        "FCTL",
        "FREQI",
        "FREQL",
        "TGCLDCWP",
        "TGCLDIWP",
        "TGCLDLWP",
        "TGCLDCWP_gm2",
        "TGCLDIWP_gm2",
        "TGCLDLWP_gm2",
        "CDNUMC",
        "CDNUMC_1e6cm2",
        "REFFCLIMODIS",
        "REFFCLWMODIS",
        "TAUIMODIS",
        "TAUTMODIS",
        "TAUWMODIS",
        "MEANCLDALB_ISCCP",
        "AREL_incld",
        "AWNC_incld",
        "ACTNL_incld",
        "ACTREL_incld",
    ],

    # -------------------------------------------------------------------------
    # Radiative fluxes and Ghan decomposition
    # -------------------------------------------------------------------------
    "RADIATIVE": [
        # Native radiation
        "FSNT",
        "FSNTC",
        "FSNTOA",
        "FSNTOAC",
        "FSNT_DRF",
        "FSNTCDRF",
        "FSNS",
        "FSNSC",
        "FSDS",
        "FSDSC",
        "FSDS_DRF",
        "FSDSCDRF",
        "FSUS_DRF",
        "FSUTADRF",
        "FSUTOA",
        "FLNT",
        "FLNTC",
        "FLNT_DRF",
        "FLNTCDRF",
        "FLNS",
        "FLNSC",
        "FLDS",
        "FLUS",
        "FLUT",
        "FLUTC",
        "SWCF",
        "LWCF",
        "SOLIN",

        # Derived Ghan variables
        "FTOT_Ghan",
        "SWTOT_Ghan",
        "LWTOT_Ghan",
        "SWDIR_Ghan",
        "LWDIR_Ghan",
        "DIR_Ghan",
        "SWCF_Ghan",
        "LWCF_Ghan",
        "NCFT_Ghan",
        "FREST_Ghan",
        "SW_rest_Ghan",
        "LW_rest_Ghan",

        "gw",
        "GRIDAREA"
    ],

    # -------------------------------------------------------------------------
    # Meteorology, surface state, hydrology, and dynamics
    # -------------------------------------------------------------------------
    "METEOROLOGY": [
        "T",
        "T_C",
        "TREFHT",
        "TREFHT_C",
        "TS",
        "SST",
        "Q",
        "QREFHT",
        "TMQ",
        "RELHUM",
        "U",
        "V",
        "U10",
        "WIND_SPEED",
        "VT100",
        "OMEGA",
        "Z3",
        "PS",
        "PRECC",
        "PRECL",
        "PRECSC",
        "PRECSL",
        "PRECT",
        "QFLX",
        "LHFLX",
        "SHFLX",
        "TAUX",
        "TAUY",
        "SNOWHICE",
        "SNOWHLND",

        # Derived chemistry-context means
        "T_trop_massmean",
        "Q_trop_massmean",
        "FSDS_global_mean",
        "SOLIN_global_mean",
        "CLDTOT_global_mean",
        "TREFHT_global_mean",
        "QREFHT_global_mean",
    ],

    # -------------------------------------------------------------------------
    # Land/area/mask and coordinate/static fields
    # -------------------------------------------------------------------------
    "GRID": [
        "LANDFRAC",
        "GRIDAREA",
        "gw",
        "lat",
        "lon",
        "lev",
        "ilev",
        "hyam",
        "hybm",
        "hyai",
        "hybi",
        "P0",
        "PS",
        "TROP_P",
        "TROP_T",
        "TROP_Z",
        "time",
        "time_bnds",
        "date",
        "datesec",
    ],

    # -------------------------------------------------------------------------
    # Map-ready diagnostics from postprocessing
    # -------------------------------------------------------------------------
    "MAPS": [
        "CH4_OH_loss_column_Tg_yr",
        "OH_trop_massmean_column",
        "O3_trop_massmean_column",
        "CO_trop_massmean_column",
        "NO_trop_massmean_column",
        "NO2_trop_massmean_column",
        "CH2O_trop_massmean_column",
        "MEG_ISOP",
        "MEG_MTERP",
        "SFISOP",
        "SFMTERP",
        "emis_ISOP",
        "emis_MTERP",
    ],
}

FORCING_MAP_VARIABLES = [
    # Native radiation fields
    "FSNT",
    "FLNT",
    "FSNT_DRF",
    "FLNT_DRF",
    "FSNTCDRF",
    "FLNTCDRF",

    # Ghan decomposition fields
    "FTOT_Ghan",       # SW_tot + LW_tot, net downward
    "SWTOT_Ghan",
    "LWTOT_Ghan",

    "SW_rest_Ghan",    # albedo / clean clear-sky SW residual
    "LW_rest_Ghan",
    "FREST_Ghan",      # SW_rest + LW_rest

    "SWCF_Ghan",       # SW cloud forcing
    "LWCF_Ghan",       # LW cloud forcing
    "NCFT_Ghan",       # SW_cloud + LW_cloud

    "SWDIR_Ghan",      # SW direct aerosol/SOA
    "LWDIR_Ghan",      # LW direct aerosol/SOA
    "DIR_Ghan",        # SW_dir + LW_dir

    # Optional native cloud radiative effects
    "SWCF",
    "LWCF",
]


BVOC_CONTEXT_MAP_VARIABLES = [
    # BVOC emissions
    "SFISOP",
    "SFMTERP",
    "MEG_ISOP",
    "MEG_MTERP",
    "emis_ISOP",
    "emis_MTERP",

    # SOA / aerosol burden
    "cb_SOA_LV",
    "cb_SOA_NA",
    "cb_SOA_SV",
    "cb_SOA_dry",
    "cb_SOA_TOT",

    # Aerosol number / activation
    "N_AER",
    "N_AER_ST",
    "NCONC01",
    "NCONC02",
    "NCONC03",
    "NCONC04",
    "NCONC05",
    "NCONC06",
    "NCONC07",
    "NCONC08",
    "NCONC09",
    "NCONC10",
    "NCONC11",
    "NCONC12",
    "NCONC13",
    "NCONC14",

    "FCTL",
    "ACTREL",
    "ACTNL",
    "ACTREL_incld",
    "ACTNL_incld",

    # Cloud liquid water
    "TGCLDLWP",
    "TGCLDLWP_gm2",
    "CLDLIQ",
    "CLDLIQ_mgkg",
    "CDNUMC",
    "CDNUMC_1e6cm2",

    # Hydrology / ET
    "QFLX",
    "QFLX_mmday",
    "LHFLX",

    # Chemistry context for the chemistry-residual interpretation
    "O3",
    "O3_SRF",
    "O3_trop_massmean",
    "O3_burden_Tg",
    "OH",
    "OH_trop_massmean",
    "CH4_lifetime_OH_yr",
    "CO_trop_massmean",
    "NOx_trop_massmean",
]

VARIABLE_CLASSES.update({
    "FORCING_MAPS": FORCING_MAP_VARIABLES,
    "BVOC_CONTEXT_MAPS": BVOC_CONTEXT_MAP_VARIABLES,
})

def catalog_variable_union() -> list[str]:
    variables: list[str] = []
    for class_vars in VARIABLE_CLASSES.values():
        variables.extend(class_vars)
    return sorted(set(variables))


__all__ = [
    "VARIABLE_CLASSES",
    "FORCING_MAP_VARIABLES",
    "BVOC_CONTEXT_MAP_VARIABLES",
    "catalog_variable_union",
]