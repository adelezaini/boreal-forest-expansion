#!/bin/bash
# 5-day LCC_PD partner of the CTRL_PD 5-day test (13a-…-meganpatch-5day.sh), for developing and testing the
# reduction + LMDI script (postprocess/megan_lmdi/) on a real CTRL + LCC pair (user OK 2026-10-29).
# BRANCH of LCC_PD (old chain, -20261005) at 2005-01-01, 5 days, with the SLIM production output:
# CAM SFISOP/SFMTERP (monthly + 30-min), CLM monthly grid-cell MEGAN fields, CLM tape 2 = 72 MEGAN fields per patch
# (PFTS), instantaneous, every time step. LCC_PD has no 30-min CAM output, so no bit-identity check here.
# Run from cases-scripts/. Checks: diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')

CASENAME="NF2000norbc_tropstratchem_nudg_lcc_f19_f19-test-meganpatch-5day-slim-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Parent run: LCC_PD, old chain (archived; restart 2005-01-01)
REFCASE="NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005"
REFDATE="2005-01-01"
PARENT_CASEROOT="$HOME/cases/BRL_FRST_XPSN/$REFCASE"

REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/${REFCASE}/rest/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
[[ -d "$PARENT_CASEROOT" ]] || { echo "ERROR: missing parent case $PARENT_CASEROOT"; exit 1; }
# Same CLM SourceMod as the parent, or the branch is not the same model
cmp -s "$PARENT_CASEROOT/SourceMods/src.clm/VOCEmissionMod.F90" "$REPO_ROOT/model/SourceMods/src.clm/VOCEmissionMod.F90" \
    || { echo "ERROR: repo VOCEmissionMod.F90 differs from the parent's"; exit 1; }

prepare_restart_files "$REST_SRC" "$REST_LOCAL"

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN/"
CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

forcings_2000

# Branch from the parent's restart (no init interpolation, model state taken as is)
./xmlchange RUN_TYPE=branch
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length: 5 days
./xmlchange STOP_OPTION=ndays,STOP_N=5
./xmlchange RESUBMIT=0
./xmlchange REST_OPTION=ndays,REST_N=5
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE

./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=02:00:00
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=01:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Nudging: only for the -offline_dyn build option; the metdata namelist comes with the parent's user_nl_cam
setup_nudging_data

# Namelists = the parent's, verbatim (no drift from later edits of cases-setup.sh)
for f in user_nl_cam user_nl_clm user_nl_cice user_nl_cpl user_nl_docn user_nl_mosart; do
    cp "$PARENT_CASEROOT/$f" "$f"
done
# A branch reads the restart directly: drop init interpolation (hybrid/startup only)
sed -i '/^ *use_init_interp *=/d' user_nl_clm
# Nudging: a branch starts the met reader from met_data_file (a continue run takes it from the restart),
# and the reader only steps one file forward: point it to the branch date, not the parent's 2000-01-01
sed -i -E "s/(met_data_file *= *'.*\.cam\.h1\.)2000-01-01-00000\.nc'/\1${REFDATE}-00000.nc'/" user_nl_cam
grep -q "cam.h1.${REFDATE}-00000.nc'" user_nl_cam || { echo "ERROR: met_data_file not set to $REFDATE"; exit 1; }

# Slim output: drop every history setting of the parent (key lines + their continuation lines)
drop_hist() {  # $1 = file, $2 = regex of keys to drop
    python3 - "$1" "$2" <<'PYDROP'
import re, sys
path, keys = sys.argv[1], re.compile(sys.argv[2])
out, skipping = [], False
for line in open(path):
    if keys.match(line):
        skipping = True
        continue
    if skipping and re.match(r"\s*'", line):   # continuation of a dropped list
        continue
    skipping = False
    out.append(line)
open(path, "w").writelines(out)
PYDROP
}
drop_hist user_nl_cam '^(fincl\d|mfilt|nhtfrq|avgflag_pertape)\b'
drop_hist user_nl_clm '^hist_'
grep -Eq "^(fincl|mfilt|nhtfrq|avgflag_pertape)" user_nl_cam && { echo "ERROR: CAM history settings left"; exit 1; }
grep -Eq "^hist_" user_nl_clm && { echo "ERROR: CLM history settings left"; exit 1; }

# CAM: only the MEGAN fluxes the atmosphere receives (monthly; 30-min for the bit-identity check).
# empty_htapes, history_aerosol, docosp stay as in the parent. Insert before the final "/" of the namelist.
python3 - user_nl_cam <<'PYCAM'
import sys
p = sys.argv[1]; lines = open(p).read().rstrip("\n").split("\n")
assert lines[-1].strip() == "/", "user_nl_cam: last line is not '/'"
lines[-1:] = ["mfilt           = 1, 48", "nhtfrq          = 0, 1", "avgflag_pertape = 'A', 'I'",
              "fincl1 = 'SFISOP','SFMTERP'", "fincl2 = 'SFISOP','SFMTERP'", "/"]
open(p, "w").write("\n".join(lines) + "\n")
PYCAM

# CLM tape 1: monthly grid-cell MEGAN fields only (no default fields); tape 2: per patch, every step, one file per day
cat << 'EOF' >> user_nl_clm

hist_empty_htapes    = .true.
hist_mfilt           = 1, 48
hist_nhtfrq          = 0, 1
hist_avgflag_pertape = 'A', 'I'
hist_dov2xy          = .true., .false.
hist_type1d_pertape  = ' ', 'PFTS'
hist_fincl1 = 'MEG_isoprene','MEG_pinene_a','MEG_carene_3','MEG_pinene_b','MEG_myrcene',
    'MEG_limonene','MEG_ocimene_t_b','MEG_sabinene','GAMMAL','GAMMAC_isoprene',
    'GAMMA_isoprene','GAMMAP_isoprene','GAMMAT_isoprene','GAMMAA_isoprene',
    'GAMMA_pinene_a','GAMMAP_pinene_a','GAMMAT_pinene_a','GAMMAA_pinene_a',
    'GAMMA_carene_3','GAMMAP_carene_3','GAMMAT_carene_3','GAMMAA_carene_3',
    'GAMMA_pinene_b','GAMMAP_pinene_b','GAMMAT_pinene_b','GAMMAA_pinene_b',
    'GAMMA_myrcene','GAMMAP_myrcene','GAMMAT_myrcene','GAMMAA_myrcene',
    'GAMMA_limonene','GAMMAP_limonene','GAMMAT_limonene','GAMMAA_limonene',
    'GAMMA_ocimene_t_b','GAMMAP_ocimene_t_b','GAMMAT_ocimene_t_b','GAMMAA_ocimene_t_b',
    'GAMMA_sabinene','GAMMAP_sabinene','GAMMAT_sabinene','GAMMAA_sabinene'
hist_fincl2 = 'MEG_isoprene','MEG_pinene_a','MEG_carene_3','MEG_pinene_b','MEG_myrcene',
    'MEG_limonene','MEG_ocimene_t_b','MEG_sabinene',
    'GAMMAL','GAMMAC_isoprene',
    'EPS_isoprene','GAMMA_isoprene','GAMMAP_isoprene','GAMMAT_isoprene','GAMMAA_isoprene',
    'EPS_pinene_a','GAMMA_pinene_a','GAMMAP_pinene_a','GAMMAT_pinene_a','GAMMAA_pinene_a',
    'EPS_carene_3','GAMMA_carene_3','GAMMAP_carene_3','GAMMAT_carene_3','GAMMAA_carene_3',
    'EPS_pinene_b','GAMMA_pinene_b','GAMMAP_pinene_b','GAMMAT_pinene_b','GAMMAA_pinene_b',
    'EPS_myrcene','GAMMA_myrcene','GAMMAP_myrcene','GAMMAT_myrcene','GAMMAA_myrcene',
    'EPS_limonene','GAMMA_limonene','GAMMAP_limonene','GAMMAT_limonene','GAMMAA_limonene',
    'EPS_ocimene_t_b','GAMMA_ocimene_t_b','GAMMAP_ocimene_t_b','GAMMAT_ocimene_t_b','GAMMAA_ocimene_t_b',
    'EPS_sabinene','GAMMA_sabinene','GAMMAP_sabinene','GAMMAT_sabinene','GAMMAA_sabinene',
    'TV','TV24','TV240','ELAI','LAI240','FSUN','FSUN24','FSUN240',
    'FSD24','FSD240','FSI24','FSI240',
    'PAR_sun','PAR24_sun','PAR240_sun','PAR_shade','PAR24_shade','PAR240_shade',
    'TOPT','EOPT','ALPHA','currentPatch'
EOF

install_clm_sourcemods

# Namelists must match the parent's except history output and start type
./preview_namelists > /dev/null
DIFF_LOG="$CASEROOT/namelist_diff_vs_parent.txt"
for f in atm_in lnd_in drv_in drv_flds_in; do
    diff <(sort "$PARENT_CASEROOT/CaseDocs/$f") <(sort "CaseDocs/$f") | grep '^[<>]' | sed "s/^/$f: /" || true
done > "$DIFF_LOG"
UNEXPECTED=$(grep -Ev "hist_|fincl|'(MEG|GAMMA|EPS|TV|ELAI|LAI240|FSUN|FSD|FSI|PAR|TOPT|EOPT|ALPHA|currentPatch)|^[a-z_]+: [<>] +'|finidat|nrevsn|cam_branch_file|met_data_file|mfilt|nhtfrq|avgflag_pertape|use_init_interp|init_interp|ncdata|start_type|case_name|caseid|brnch_retain_casename|restart_|start_ymd|start_tod|stop_|rest_|ref_ymd|ref_tod|orb_|username|hostname|model_version|case_desc" "$DIFF_LOG" || true)
if [[ -n "$UNEXPECTED" ]]; then
    echo "ERROR: namelists differ from the parent beyond history/start settings (full list: $DIFF_LOG):"
    echo "$UNEXPECTED"
    exit 1
fi
echo "Namelist diff vs parent (history/start settings only): $DIFF_LOG"

./case.build
./case.submit
