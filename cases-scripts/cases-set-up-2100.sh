#!/bin/bash

# Aerosol diagnostics
./xmlchange CAM_AEROCOM=TRUE

# NORBC - fSST
./xmlchange SSTICE_DATA_FILENAME=/cluster/shared/noresm/inputdata/noresm-only/atm/cam/sst/fice-micom-divocn_sst-micom-dow_NSSP585frc2_f19_tn14_20191014_2090-2100_series_version20260209_clim.nc
./xmlchange OCN_FLUX_SCHEME=1

# COSP diagnostics
./xmlchange --append CAM_CONFIG_OPTS='-cosp'
cat << EOF >> user_nl_cam
&cospsimulator_nl
  docosp    = .true.
  cosp_amwg = .true.
/
EOF

# DMS forcing to 2000
cat << EOF >> user_nl_cam
&oslo_ctl_nl
  ocean_filename = 'dms-hamocc-dow-taylor_chlor_a-lanaclim_NHIST_f19_tn14_20190710_1995-2005_cycle_version20260209.nc'
  ocean_filepath = '/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo'
/
EOF