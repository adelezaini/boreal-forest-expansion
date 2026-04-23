
import numpy as np

atm_always_include = ['LANDFRAC', 'GRIDAREA', 'gw', 'date', 'time_bnds', 'T', 'TS', 'U', 'V']
lnd_always_include = ['area', 'landfrac', 'landmask', 'pftmask', 'PCT_LANDUNIT']
pressure_variables = ['P0', 'hyam', 'hybm', 'PS', 'hyai', 'hybi', 'ilev']
Ghan_vars = ['SWDIR', 'LWDIR', 'DIR', 'SWCF', 'LWCF', 'NCFT', 'SW_rest', 'LW_rest', 'FREST', 'FTOT', 'SWTOT', 'LWTOT']

def variables_by_component(comp, bvoc=True):
    """Return dict of selected variables per cathegory given the respective component"""

    if comp == 'atm':

        variables = \
            {'BVOC': ['SFisoprene', 'SFmonoterp'],
             'SOA': ['N_AER', 'DOD550', 'SOA_A1','SOA_NA','cb_SOA_A1','cb_SOA_NA', 'cb_SOA_A1_OCW', 'cb_SOA_NA_OCW', 'NUCLRATE', 'FORMRATE', 'CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B', 'cb_H2SO4','cb_SOA_LV', 'H2SO4', 'SOA_LV'],
             'CLOUDPROP': ['ACTNL', 'ACTREL','AREL', 'AWNC', 'CDNUMC', 'CLDHGH', 'CLDLOW', 'CLDMED', 'CLDTOT', 'CLDLIQ', 'CLOUD',
                           'CLOUDCOVER_CLUBB', 'FCTL', 'FREQL', 'NUMLIQ', 'TGCLDCWP', 'TGCLDLWP', 'TGCLDIWP'],
             'RADIATIVE': ['FSDS','FSNS','FLNT', 'FSNT', 'FLNT_DRF', 'FLNTCDRF', 'FSNTCDRF', 'FSNT_DRF', 'LWCF', 'SWCF', 'LHFLX', 'SHFLX'], #, 'OMEGAT'
             }
        """
        FSDS = “Downwelling solar flux at surface”
        FSDSC = “Clearsky downwelling solar flux at surface”
        FSDSCDRF = “SW downwelling clear sky flux at surface”
        FSDS_DRF = “SW downelling flux at surface”
        FSNS = “Net solar flux at surface”
        FSNSC = “Clearsky net solar flux at surface”
        FSNT = “Net solar flux at top of model”
        FSNTC = “Clearsky net solar flux at top of model”
        FSNTOA = “Net solar flux at top of atmosphere”
        FSNTOAC = “Clearsky net solar flux at top of atmosphere”
        FSUS_DRF = “SW upwelling flux at surface”
        FSUTADRF = “SW upwelling flux at TOA”
        FSUTOA
        """

    elif comp =='lnd':

        lnd_vars = ['TSA', 'Q2M', 'RH2M', 'PCT_NAT_PFT', 'TLAI']
        biogeochem_vars = ['GPP', 'NPP', 'NEE', 'NEP', 'STORVEGN', 'TOTPFTN', 'TOTVEGN',
                'TOTCOLC', 'TOTECOSYSC', 'TOTPFTC', 'TOTVEGC', 'STORVEGC']
        evap_vars = ['QFLX_EVAP_TOT', 'FCEV', 'FCTR', 'FGEV', 'QSOIL', 'QVEGE', 'QVEGT']

        if bvoc: #casename.find('OFF')<0.:
            variables = {'LAND': lnd_vars,
                        'BIOGEOCHEM': ['MEG_isoprene', 'MEG_limonene', 'MEG_myrcene', 'MEG_ocimene_t_b',
                                  'MEG_pinene_a', 'MEG_pinene_b', 'MEG_sabinene'] + biogeochem_vars,
                        'ET': evap_vars}
        else:
            variables = {'LAND': lnd_vars,
                        'BIOGEOCHEM': biogeochem_vars,
                        'ET': evap_vars}
            
    return variables
