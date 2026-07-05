# BRL-FRST-XPSN
Notebooks and scripts for the paper "Climatic impacts of the Arctic expansion of boreal forests".

This repository contains all files to document the work and have it reproducible, from the model setup to the output analysis.

## File organization

- `brl_frst_xpsn`: contains all the code - preprocessing the input files of the perturbed vegetation configuration, postprocessing the raw model outputs, analysing the post-processed data
  - `data`: stores input and output processed data
  - `figures`: illustrates analyzed results
  - `noresm-scripts`: scripts to reproduce the simulations in NorESM2
  - `noresm-inputdata`: input files needed to run the simulations in NorESM2

## Useful path in Betzy (or NIRD, accessed from Betzy):

- `/cluster/projects/nn9188k/adelez/restart`: initial files of spinups (originally from /nird/datalake/NS9560K/olivie/restart/)
  - `/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_78pfts_LPJGUESS_SSP585.nc`: surface data file with PFT distribution from LPJGUESS, forced with GFDL-ESM4 in SSP5-8.5 
- `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/`: after copied cases from /cluster/work/users/adelez/archive
  - `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$casename/rest`: restart files for next simulations
  - `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$casename/cpl/hist`: auxiliary files to force climate in land-only simulations
  - `/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$casename/atm/hist` or `land/hist`: history files with raw outputs
