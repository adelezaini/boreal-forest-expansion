#!/bin/bash

### MET extension: continuation of MET (12a) for 2015-01-01 -> 2026-01-02
# MET = NF2000norbc_tropstratchem_met_f19_f19_20260422: free NF2000 run (no nudging) that
# writes the 6-hourly PS/U/V/T/Q (h1) used to nudge every PD and FUT run. 12a covered
# 2000-01-01 -> 2015-01-01. This script continues it exactly (RUN_TYPE=branch from its own
# restart). User decisions 2026-11-03:
#   - 11 more years, 2015-2025; stop at 2026-01-02 so the met files have records after
#     2026-01-01 00:00 (nudged runs can end on 2026-01-01 without patching a file);
#   - keep the MET case name (BRNCH_RETAIN_CASENAME): one file prefix for 2000-2025;
#   - minimal h0 like the spin-ups (cam_met_diagnostics, clm_spinup_diagnostics);
#   - 10-day reproduction test first.
# Build, PEs and every non-history namelist key are checked against the archived MET case
# before building: the model must be the same one that made 2000-2014.
#
# Usage (from cases-scripts/):
#   bash 12d-...sh test         10-day reproduction test: branch from MET 2010-01-01
#                               (MET only kept restarts 2005/2010/2015), new case name;
#                               check with preprocess/nudging/check_met_reproduction.py
#   bash 12d-...sh production   the 11-year extension, case name = MET
# Add --no-submit to stop after case.build (to inspect the case).

set -euo pipefail
source cases-setup.sh

MODE="${1:-}"
SUBMIT=1
[[ "${2:-}" == "--no-submit" ]] && SUBMIT=0
[[ "$MODE" == "test" || "$MODE" == "production" ]] || { echo "Usage: $0 test|production [--no-submit]" >&2; exit 1; }

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
MET="NF2000norbc_tropstratchem_met_f19_f19_20260422"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

MET_ARCHIVE="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$MET"
MET_CASE_ARCHIVED="$MET_ARCHIVE/case/$MET"     # case dir of the 2000-2014 run

if [[ "$MODE" == "test" ]]; then
    CASENAME="NF2000norbc_tropstratchem_met_reprotest_f19_f19-$today"
    REFDATE="2010-01-01"
else
    CASENAME="$MET"
    REFDATE="2015-01-01"
fi
REST_SRC="$MET_ARCHIVE/rest/${REFDATE}-00000"
# Staged on /cluster/work: home is near its quota (unzipped restart ~6 GB)
REST_LOCAL="/cluster/work/users/$USER/restart/$MET/${REFDATE}-00000"
CASEROOT="$HOME/cases/BRL_FRST_XPSN/$CASENAME"
WORK_ARCHIVE="/cluster/work/users/$USER/archive/$CASENAME"
RUNROOT_CASE="/cluster/work/users/$USER/noresm/$CASENAME"

# Keys allowed to differ from the archived MET namelists: history output, restart/branch
# bookkeeping, run length. Everything else must match.
ALLOWED_NML_KEYS='empty_htapes|fincl1|ncdata|cam_branch_file|finidat|nrevsn|hist_[a-z0-9_]+|use_init_interp|ice_ic|runtype|brnch_retain_casename|case_name|case_desc|start_type|start_ymd|start_tod|stop_n|stop_option|stop_ymd|stop_tod|restart_n|restart_option|restart_ymd|restart_file|force_stop_at|finidat_rtm|nrevsn_rtm|ref_ymd|ref_tod|timing_dir|tchkpt_dir|username|hostname|model_version|model_doi_url'

#––––––––––– SAFETY CHECKS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
[[ -d "$MET_CASE_ARCHIVED/CaseDocs" ]] || { echo "ERROR: missing archived MET case: $MET_CASE_ARCHIVED" >&2; exit 1; }
[[ ! -e "$CASEROOT" ]]     || { echo "ERROR: case dir exists, not touching it: $CASEROOT" >&2; exit 1; }
[[ ! -e "$WORK_ARCHIVE" ]] || { echo "ERROR: work archive exists, not touching it: $WORK_ARCHIVE" >&2; exit 1; }
if [[ "$MODE" == "production" && -e "$RUNROOT_CASE" ]]; then
    # Leftover from the April run: only symlinks to the spin-up refcase files. Moved, not deleted.
    echo "Moving leftover run dir $RUNROOT_CASE -> ${RUNROOT_CASE}_leftover-$today"
    mv "$RUNROOT_CASE" "${RUNROOT_CASE}_leftover-$today"
fi

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
stage_branch_restart "$REST_SRC" "$REST_LOCAL"
grep -q "$MET.cam.r.${REFDATE}-00000.nc" "$REST_LOCAL/rpointer.atm" \
    || { echo "ERROR: rpointer.atm does not point to $REFDATE" >&2; exit 1; }
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
cd $NORESM_ROOT/cime/scripts || exit 1
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT
echo "Case $CASENAME created with compset $COMPSET and resolution $RES"
cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Same build as MET: copy its CAM options exactly (12a used aerosol_cosp_diagnostics,
# no longer in cases-setup.sh: CAM_AEROCOM=TRUE + -cosp)
./xmlchange CAM_CONFIG_OPTS="$(./xmlquery --caseroot "$MET_CASE_ARCHIVED" --value CAM_CONFIG_OPTS)"
./xmlchange CAM_AEROCOM="$(./xmlquery --caseroot "$MET_CASE_ARCHIVED" --value CAM_AEROCOM)"
forcings_2000

# Branch = exact continuation from the MET restart
./xmlchange RUN_TYPE=branch
./xmlchange RUN_REFCASE="$MET"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE
./xmlchange RUN_STARTDATE="$REFDATE"

if [[ "$MODE" == "test" ]]; then
    ./xmlchange STOP_OPTION=ndays,STOP_N=10,RESUBMIT=0
    ./xmlchange REST_OPTION=never
    ./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=01:30:00
    ./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=00:30:00
else
    # brnch_retain_casename: no xml var in this CIME; the driver sets it to .true. by itself
    # when CASE == RUN_REFCASE in a branch run (checked in drv_in after preview_namelists)
    # 6 yr + 6 yr segments, cut at 2026-01-02 by STOP_DATE: 2015->2021, 2021->2026-01-02
    ./xmlchange STOP_OPTION=nyears,STOP_N=6,STOP_DATE=20260102,RESUBMIT=1
    ./xmlchange REST_OPTION=nyears,REST_N=1
    # 6.78 simulated_years/day for MET -> ~21 h per 6-yr segment
    ./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=48:59:00
    ./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
fi

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Output: h1 6-hourly nudging tape (as in MET) + minimal h0 (user 2026-11-03)
cam_met_diagnostics
clm_spinup_diagnostics

# Same model as MET? Stop before building if not.
./preview_namelists > /dev/null
compare_xml_to_archived_case "$MET_CASE_ARCHIVED"
compare_namelists_to_archived_case "$MET_CASE_ARCHIVED/CaseDocs" "$ALLOWED_NML_KEYS"
if [[ "$MODE" == "production" ]]; then
    grep -Eq "brnch_retain_casename *= *\.true\." CaseDocs/drv_in \
        || { echo "ERROR: brnch_retain_casename is not .true. in drv_in" >&2; exit 1; }
fi

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
if [[ $SUBMIT -eq 1 ]]; then
    ./case.submit
else
    echo "Built, not submitted (--no-submit). Submit with: cd $CASEROOT && ./case.submit"
fi
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
