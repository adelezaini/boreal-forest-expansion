#!/bin/bash

### LCC_FUT_HRBVOC: output-only rerun of LCC_FUT (24a, -20261028) that writes the 30-min BVOC h1
# Why (user 2026-11-04): if 14e fails the matched-baseline assumption, design A in FUT needs
# LCC_FUT_fBVOClccFUT, i.e. half-hourly emissions from LCC_FUT, which 24a did not write
# (no HR_BVOC_ALL). Started ahead of the 14e verdict to gain a day.
# Same model, inputs and restarts as LCC_FUT; only the history output differs:
#   h1 = 30-min SFISOP, SFMTERP + 6 short-lived MEG_* (as HR_BVOC_ALL)
#   h0 = SFISOP, SFMTERP monthly, only to prove bit-identity with LCC_FUT h0
#   no CLM history. The 11 monthly MEG_* come from LCC_FUT's own h0.
# Three parallel segments (LCC_FUT kept restarts only at 2005, 2010, 2015):
#   s1  hybrid from the LCC_FUT spin-up 0021-01-01 (exactly as 24a), 2000-2004
#   s2  branch from LCC_FUT 2005-01-01, 2005-2009
#   s3  branch from LCC_FUT 2010-01-01, 2010-2014
# Exception to the 15-yr rule per case (user OK 2026-11-04): together they cover 2000-2014.
# Merge for the emission builder: preprocess/bvoc-emissions/merge_lcc_fut_hrbvoc.sh.
#
# Usage (from cases-scripts/): bash 24f-...sh s1|s2|s3 [--no-submit]

set -euo pipefail
source cases-setup.sh

SEG="${1:-}"
SUBMIT=1
[[ "${2:-}" == "--no-submit" ]] && SUBMIT=0
case "$SEG" in
    s1) REFDATE_BRANCH="" ;;
    s2) REFDATE_BRANCH="2005-01-01" ;;
    s3) REFDATE_BRANCH="2010-01-01" ;;
    *)  echo "Usage: $0 s1|s2|s3 [--no-submit]" >&2; exit 1 ;;
esac

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
COMPSET=NF2100ssp585norbc_tropstratchem
set_project_noresm_res_vars

LCC_FUT="NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028"
LCC_FUT_CASEROOT="$HOME/cases/BRL_FRST_XPSN/$LCC_FUT"
LCC_FUT_ARCHIVE="/cluster/work/users/$USER/archive/$LCC_FUT"
CASENAME="NF2100ssp585norbc_tropstratchem_nudg_lcc_HRBVOC_f19_f19-$today-$SEG"
CASEROOT="$HOME/cases/BRL_FRST_XPSN/$CASENAME"
WORK_ARCHIVE="/cluster/work/users/$USER/archive/$CASENAME"

# As 24a
SPINUP="NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025"
SPINUP_DATE="0021-01-01"
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"

# Keys allowed to differ from LCC_FUT's namelists: history output, branch/restart bookkeeping,
# run length. Everything else must match (same model).
ALLOWED_NML_KEYS='met_data_file|empty_htapes|fincl1|fincl2|mfilt|nhtfrq|avgflag_pertape|ncdata|cam_branch_file|finidat|nrevsn|hist_[a-z0-9_]+|use_init_interp|init_interp_method|ice_ic|runtype|brnch_retain_casename|case_name|case_desc|start_type|start_ymd|start_tod|stop_n|stop_option|stop_ymd|stop_tod|restart_n|restart_option|restart_ymd|restart_file|force_stop_at|finidat_rtm|nrevsn_rtm|ref_ymd|ref_tod|timing_dir|tchkpt_dir|username|hostname|model_version|model_doi_url'

#––––––––––– SAFETY CHECKS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
[[ -d "$LCC_FUT_CASEROOT/CaseDocs" ]] || { echo "ERROR: missing LCC_FUT case: $LCC_FUT_CASEROOT" >&2; exit 1; }
[[ ! -e "$CASEROOT" ]]     || { echo "ERROR: case dir exists, not touching it: $CASEROOT" >&2; exit 1; }
[[ ! -e "$WORK_ARCHIVE" ]] || { echo "ERROR: work archive exists, not touching it: $WORK_ARCHIVE" >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]]  || { echo "ERROR: missing surfdata: $SURFDATA_FILE" >&2; exit 1; }

#––––––––––– RESTARTS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
if [[ "$SEG" == "s1" ]]; then
    REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$SPINUP/rest/$SPINUP_DATE-00000"
    REST_LOCAL="/cluster/home/$USER/restart/${SPINUP}/${SPINUP_DATE}-00000"
    prepare_restart_files "$REST_SRC" "$REST_LOCAL"
    [[ -f "$REST_LOCAL/$SPINUP.clm2.r.$SPINUP_DATE-00000.nc" ]] || { echo 'Missing coupled LCC land restart' >&2; exit 1; }
else
    REST_SRC="$LCC_FUT_ARCHIVE/rest/${REFDATE_BRANCH}-00000"
    REST_LOCAL="/cluster/work/users/$USER/restart/$LCC_FUT/${REFDATE_BRANCH}-00000"
    stage_branch_restart "$REST_SRC" "$REST_LOCAL"
    grep -q "$LCC_FUT.cam.r.${REFDATE_BRANCH}-00000.nc" "$REST_LOCAL/rpointer.atm" \
        || { echo "ERROR: rpointer.atm does not point to $REFDATE_BRANCH" >&2; exit 1; }
fi

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
cd $NORESM_ROOT/cime/scripts || exit 1
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT
echo "Case $CASENAME created with compset $COMPSET and resolution $RES"
cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# As 24a
forcings_2100
dms_forcing_2100_to_2000
setup_nudging_data "${REFDATE_BRANCH:-2000-01-01}"   # branch: met file of its start date

if [[ "$SEG" == "s1" ]]; then
    # Exactly as 24a
    ./xmlchange RUN_TYPE=hybrid
    ./xmlchange RUN_REFCASE="$SPINUP"
    ./xmlchange RUN_REFDATE="$SPINUP_DATE"
    ./xmlchange RUN_STARTDATE=2000-01-01
else
    # Exact continuation of LCC_FUT from its own restart
    ./xmlchange RUN_TYPE=branch
    ./xmlchange RUN_REFCASE="$LCC_FUT"
    ./xmlchange RUN_REFDATE="$REFDATE_BRANCH"
    ./xmlchange RUN_STARTDATE="$REFDATE_BRANCH"
fi
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# One 5-yr job per segment (~16 h at LCC_FUT's 7.4 yr/day); yearly restarts so a crash can continue
./xmlchange STOP_OPTION=nyears,STOP_N=5,RESUBMIT=0
./xmlchange REST_OPTION=nyears,REST_N=1
./xmlchange --subgroup case.run        JOB_QUEUE=normal
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=30:00:00
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
hist_empty_htapes = .true.
EOF
# use_init_interp only where 24a used it (hybrid start from finidat); a branch reads the exact CLM restart
[[ "$SEG" == "s1" ]] && echo "use_init_interp = .true." >> user_nl_clm

cam_diagnostics HR_BVOC_ONLY
install_clm_sourcemods
cmp "$LCC_FUT_CASEROOT/SourceMods/src.clm/VOCEmissionMod.F90" SourceMods/src.clm/VOCEmissionMod.F90 \
    || { echo "ERROR: CLM SourceMod differs from LCC_FUT's" >&2; exit 1; }

# Same model as LCC_FUT? Stop before building if not.
./preview_namelists > /dev/null
compare_xml_to_archived_case "$LCC_FUT_CASEROOT"
compare_namelists_to_archived_case "$LCC_FUT_CASEROOT/CaseDocs" "$ALLOWED_NML_KEYS"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
if [[ $SUBMIT -eq 1 ]]; then
    ./case.submit
else
    echo "Built, not submitted (--no-submit). Submit with: cd $CASEROOT && ./case.submit"
fi
