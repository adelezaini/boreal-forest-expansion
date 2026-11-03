#!/bin/bash

### CTRL_PD_fBVOCctrlPD_HR RUN (diagnostic: replay of CTRL_PD's actual emissions, year by year)
# Same as CTRL_PD_fBVOCctrlPD (14c), but the 19 prescribed species are CTRL_PD's ACTUAL emissions of each year
# (2000, 2001, 2002) instead of the 2001-2014 climatology. Question: does the +3 % SOA of 14c vs CTRL_PD come from
# the climatology (it disappears here) or from prescribing itself (it stays)? User OK 2026-10-29; 3 yr, 2000 dropped.
#   Files: <EMS_BASE>_<Y>-<Y>_{SFISOP,SFMTERP,MEG_*}.nc, made with
#   preprocess/bvoc-emissions/run_bvoc_climatology_array.sh <CTRL_PD case> Y Y (a one-year "climatology", stamped 2000).
#   srf_emis_type = CYCLICAL (cycle year 2000) holds for every surface-emission file, so a multi-year series is not
#   possible without changing the anthropogenic files too: the run goes in 1-year jobs and replay_prerun.sh
#   (CIME PRERUN_SCRIPT, runs before the namelists are written in every job) points user_nl_cam to that year's files.
#   h1: 30-min SFISOP, SFMTERP (HR_BVOC) to check step by step that the run received CTRL_PD's flux.
# Old chain on purpose, like 14c: REFCASE and EMS_BASE stay pinned (not set by auto_launch).

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_HR_f19_f19-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics (as 14c and CTRL_PD -20261023):
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

# PD surface data (CTRL land cover), as in 13a
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc"

# Prescribed BVOC files of each year: <EMS_BASE>_<Y>-<Y>_SFISOP.nc, ..._MEG_<species>.nc (19 per year)
EMS_BASE="/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023"
YEARS=(2000 2001 2002)

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

[[ -f "$REST_LOCAL/$REFCASE.clm2.r.$REFDATE-00000.nc" ]] || { echo 'Missing coupled CTRL land restart' >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]] || { echo "Missing surfdata: $SURFDATA_FILE" >&2; exit 1; }
for y in "${YEARS[@]}"; do
    n_ems=$(ls "${EMS_BASE}_${y}-${y}"_SF*.nc "${EMS_BASE}_${y}-${y}"_MEG_*.nc 2>/dev/null | wc -l)
    (( n_ems == 19 )) || { echo "Expected 19 prescribed BVOC files ${EMS_BASE}_${y}-${y}_*.nc, found $n_ems" >&2; exit 1; }
done

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN/"
CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

cd $NORESM_ROOT/cime/scripts

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

forcings_2000
setup_nudging_data

# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length: three 1-year jobs (2000-2002); 2000 dropped as spin-up -> compare 2001-2002 with CTRL_PD
./xmlchange STOP_OPTION=nyears,STOP_N=1
./xmlchange RESUBMIT=2
./xmlchange REST_OPTION=nyears,REST_N=1
./xmlchange RUN_STARTDATE=2000-01-01

./xmlchange --subgroup case.run JOB_QUEUE=normal
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=08:00:00
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cam_diagnostics HR_BVOC
install_clm_sourcemods
clm_diagnostics fBVOC

# Disable all interactive MEGAN and prescribe all 19 MEGAN-fed species from CTRL_PD (year-2000 files first).
prescribed_bvoc_emissions_all 2000 "${EMS_BASE}_${YEARS[0]}-${YEARS[0]}"

# The prescribed ISOP already contains its diurnal cycle.
bypass_isoprene_diurnal_adjustment

# Before every job: point the 19 BVOC entries of user_nl_cam to the files of the year the job starts in.
cat << EOF > replay_prerun.sh
#!/bin/bash
# PRERUN_SCRIPT of $CASENAME (written by 14d). Argument: CASEROOT.
set -euo pipefail
cd "\$1"
BASE="$EMS_BASE"
if [[ \$(./xmlquery --value CONTINUE_RUN) == FALSE ]]; then
    y=\$(./xmlquery --value RUN_STARTDATE | cut -c1-4)
else
    rp="\$(./xmlquery --value RUNDIR)/rpointer.atm"
    y=\$(grep -oE 'cam\.r\.[0-9]{4}' "\$rp" | head -1 | cut -c7-10)
fi
[[ " ${YEARS[*]} " == *" \$y "* ]] || { echo "replay_prerun: year '\$y' has no BVOC files" >&2; exit 1; }
sed -i -E "s#(\${BASE##*/}_)[0-9]{4}-[0-9]{4}_#\1\${y}-\${y}_#" user_nl_cam
n=\$(grep -c -- "-> \${BASE}_\${y}-\${y}_" user_nl_cam)
[[ \$n -eq 19 ]] || { echo "replay_prerun: expected 19 entries for \$y in user_nl_cam, found \$n" >&2; exit 1; }
for f in \$(grep -oE "\${BASE}_\${y}-\${y}_[A-Z0-9_]+\.nc" user_nl_cam); do
    [[ -f \$f ]] || { echo "replay_prerun: missing \$f" >&2; exit 1; }
done
echo "replay_prerun: \$(date) job starts in \$y -> BVOC files \${BASE##*/}_\${y}-\${y}_*.nc"
EOF
chmod +x replay_prerun.sh
./xmlchange PRERUN_SCRIPT="$CASEROOT/replay_prerun.sh"
./replay_prerun.sh "$CASEROOT"   # test once: must select 2000

./case.build
./case.submit
