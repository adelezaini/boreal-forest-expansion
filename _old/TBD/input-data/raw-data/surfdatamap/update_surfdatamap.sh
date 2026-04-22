#Input land files is needed to be preprocessed for idealized and realistic cases
#with the compset: 2000_CAM60%NORESM%SEC%NORPDDMSBC%SDYN_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
#the surfdata_map is: /cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc

#This file is copied in this directory (BRL-FRST-XPSN/brl_frst_xpsn/data/surfdatamap)
#In case of changing compset or any other update to the file, this is what is needed to do.

scp adelez@betzy.sigma2.no:/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc .
