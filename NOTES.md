### In cleaning process:
- cases in /cluster/home/adelez/restart/restart-archive
- .ipynb_checkpoints (17 folders) + __pycache__ (15 folders)
- old figure/table sets in results/:
    figures-pre-reorg-20261108, figures-pre-co2-fix, *-2001-2014-all-bvoc-pre-co2-fix, *-designB-standin-20261111
    --> figures-2001-2014 / tables-2001-2014: move to NIRD, don't delete
- test cases in /cluster/work/users/adelez/archive: *-test-1day, *-test-meganpatch-5day-*, *-test-hrbvocall-*, *-test-new-diagnostics
- old-chain cases (-20260924 / -20260925) still in /cluster/work archive
- .git is 4.2G --> git gc after the pending push
- results/pptx 287M (old deck versions?)

### Notes:
- first spinups: startrunyear = 0001-01-01 instead of 0000-01-01 
    --> so all years start from 0021-01-01 instead of 0020-01-01 (as the other simulations)
- equilibrium scripts are not tested

- MET doesn't need 1-year of spinup -> just CTRL & CO. I'm just continuing the spinup, no change. While CTRL & CO change the nudging...

- DMS for the FUT is not set to PD values as planned.

- found that CO2 prescribed in FUT spin-ups to PD conditions: LCC − CTRL has a tropical signal that is not from the land change
- prescribing BVOC changes the result by itself (CTRL_PD_fBVOCctrlPD: SOA +3%) --> compare LCC_*_fBVOC* with CTRL_*_fBVOC* (matched baseline), not with CTRL
- SF* = everything the atmosphere gets (MEGAN + prescribed); MEG_* = only interactive MEGAN
- added all compounds read by CAM from interactive MEGAN emissions
- runs start in 2000, but 2000 is spin-up --> the first 12 monthly records are thrown away
    
- final ems_* files go to /cluster/shared/.../bvoc_emissions, original are left in work directory and delected after 42 days

- nudging: last met file of the 2000-2015 series (`…cam.h1.2015-01-01-00000.nc`) had only 1 record (00:00) 
    --> patched 23 Oct with `preprocess/nudging/extend_last_met_file.py`: added the 06/12/18 h records, copied from 2014-12-31 (only drive the model past the stop date, output unaffected)

- GAMMA_* is an area mean over vegetated patches, not emission-weighted; EPS/GAMMA only for 7 of 21 MTERP

- MEGAN LMDI, 2000-chain years (2001, 2002): steps were put in the month one 30-min step off (tape-2 days 00:00-23:30)
