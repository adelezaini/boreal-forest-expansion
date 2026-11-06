#!/bin/bash
# MEGAN exact split (analysis/MEGAN_ATTRIBUTION.md, option 1): production branch case.
# BRANCH of a new-chain nudged run (CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT) from its archived restart at START_DATE,
# same model and namelists, only the history output changes (SLIM, user 2026-10-29):
#   CAM  h0 monthly SFISOP/SFMTERP, h1 30-min SFISOP/SFMTERP (identity check with the parent)
#   CLM  h0 monthly grid-cell MEG_*/GAMMA* (hist_empty_htapes), h1 = tape 2: 72 MEGAN fields per patch (PFTS),
#        instantaneous, every 30-min step, one file per day (≈ 0.6 GB/day)
# Template: cases-scripts/tests/13a-…-meganpatch-5day.sh (5-day test, identity passed 29 Oct).
#
# Years (user 2026-11-04): the parents kept restarts only at 2005, 2010, 2015, so each run has CHAINS,
# one case each: from 2000 (hybrid from the spin-up as the parent; 2000 deleted, 2001–2003 used; user 2026-11-04),
# from 2005 (2005–2008), from 2010 (2010–2012), [from 2015 (2015–2017, not planned; needs the met folder
# _6h_2000-2025 and, for the identity check, the parents' 2015–2025 extension)]. One model year per job (≈ 14 h);
# the launcher sets RESUBMIT / CONTINUE_RUN per batch. Mode --days N [--resubmit K] = short test: K+1 jobs of N days
# (production test, user 2026-11-04: 2 x 30 days from 2005-01-01 = 2 months + 1 day, restart mid-run).
#
# Creates and BUILDS the case, never submits (launch_megan_lmdi.sh submits, after the user's OK).
# Usage (from anywhere): bash branch_meganpatch.sh CTRL_PD|LCC_PD|CTRL_FUT|LCC_FUT START_DATE [--days N] [--check-only]
#   e.g. bash branch_meganpatch.sh CTRL_PD 2005-01-01            -> …_meganpatch_f19_f19-<today>-from2005
#        bash branch_meganpatch.sh LCC_PD 2005-01-01 --days 32   -> …_meganpatch_f19_f19-<today>-test32d
# Prints the case name on the last line ("CASE <name>").

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../cases-setup.sh"

RUN="${1:-}"; START_DATE="${2:-}"
DAYS=""; CHECK_ONLY=0; NRESUB=0
shift 2 || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --days) DAYS="${2:?--days needs a number}"; shift 2 ;;
        --resubmit) NRESUB="${2:?--resubmit needs a number}"; shift 2 ;;   # test only: K more jobs of N days
        --check-only) CHECK_ONLY=1; shift ;;      # stop after the comparison with the parent (no build); for testing
        *) echo "unknown option $1" >&2; exit 1 ;;
    esac
done
[[ "$START_DATE" =~ ^[0-9]{4}-01-01$ ]] || { echo "Usage: $0 RUN YYYY-01-01 [--days N]" >&2; exit 1; }

#––––––––––– PARENTS (new chain; CLAUDE.md versions table) ––––––––––––––––––––––––––––––––––––––––––––––––––––
case "$RUN" in
    CTRL_PD)  PARENT="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029";      COMPSET=NF2000norbc_tropstratchem ;;
    LCC_PD)   PARENT="NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028";       COMPSET=NF2000norbc_tropstratchem ;;
    CTRL_FUT) PARENT="NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028"; COMPSET=NF2100ssp585norbc_tropstratchem ;;
    LCC_FUT)  PARENT="NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028";  COMPSET=NF2100ssp585norbc_tropstratchem ;;
    *) echo "Usage: $0 CTRL_PD|LCC_PD|CTRL_FUT|LCC_FUT YYYY-01-01 [--days N]" >&2; exit 1 ;;
esac
today=$(date +'%Y%m%d')
set_project_noresm_res_vars
YEAR=${START_DATE:0:4}
TAG=$([[ -n "$DAYS" ]] && echo "test$(( DAYS * (NRESUB + 1) ))d" || echo "from$YEAR")
CASENAME="${PARENT%-*}"; CASENAME="${CASENAME/_f19_f19/_meganpatch_f19_f19}-$today-$TAG"
PARENT_CASEROOT="$HOME/cases/BRL_FRST_XPSN/$PARENT"
CASEROOT="$HOME/cases/BRL_FRST_XPSN/$CASENAME"
WORK_ARCHIVE="/cluster/work/users/$USER/archive/$CASENAME"
REST_SRC="/cluster/work/users/$USER/archive/$PARENT/rest/${START_DATE}-00000"
REST_LOCAL="/cluster/work/users/$USER/restart/$PARENT/${START_DATE}-00000"

# Keys allowed to differ from the parent's namelists: history output, branch/restart bookkeeping, run length
ALLOWED_NML_KEYS='met_data_file|met_filenames_list|empty_htapes|fincl[0-9]|mfilt|nhtfrq|avgflag_pertape|ncdata|cam_branch_file|finidat|nrevsn|hist_[a-z0-9_]+|use_init_interp|init_interp_method|ice_ic|runtype|brnch_retain_casename|case_name|case_desc|start_type|start_ymd|start_tod|stop_n|stop_option|stop_ymd|stop_tod|restart_n|restart_option|restart_ymd|restart_file|force_stop_at|finidat_rtm|nrevsn_rtm|ref_ymd|ref_tod|timing_dir|tchkpt_dir|username|hostname|model_version|model_doi_url'

#––––––––––– SAFETY CHECKS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
[[ -d "$PARENT_CASEROOT/CaseDocs" ]] || { echo "ERROR: missing parent case: $PARENT_CASEROOT" >&2; exit 1; }
[[ ! -e "$CASEROOT" ]]     || { echo "ERROR: case dir exists, not touching it: $CASEROOT" >&2; exit 1; }
[[ ! -e "$WORK_ARCHIVE" ]] || { echo "ERROR: work archive exists, not touching it: $WORK_ARCHIVE" >&2; exit 1; }
if [[ "$START_DATE" == 2000-01-01 ]]; then
    # 2000 chain (user 2026-11-04): start exactly as the parent did, HYBRID from its coupled spin-up restart
    # (precedent: LCC_FUT_HRBVOC s1, bit-identical to LCC_FUT). Year 2000 = spin-up year, deleted unreduced.
    HYBRID=1
    SPINUP=$(cd "$PARENT_CASEROOT" && ./xmlquery --value RUN_REFCASE)
    SPINUP_DATE=$(cd "$PARENT_CASEROOT" && ./xmlquery --value RUN_REFDATE)
    [[ "$(cd "$PARENT_CASEROOT" && ./xmlquery --value RUN_TYPE)" == hybrid ]] || { echo "ERROR: parent is not hybrid" >&2; exit 1; }
    REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$SPINUP/rest/${SPINUP_DATE}-00000"
    REST_LOCAL="/cluster/home/$USER/restart/$SPINUP/${SPINUP_DATE}-00000"
    prepare_restart_files "$REST_SRC" "$REST_LOCAL"
    [[ -f "$REST_LOCAL/$SPINUP.clm2.r.${SPINUP_DATE}-00000.nc" ]] || { echo "ERROR: missing spin-up land restart" >&2; exit 1; }
else
    HYBRID=0
    [[ -n "$(ls -A "$REST_SRC" 2>/dev/null)" ]] \
        || { echo "ERROR: no restart files in $REST_SRC (the parents kept only 2005, 2010, 2015)" >&2; exit 1; }
    stage_branch_restart "$REST_SRC" "$REST_LOCAL"
    grep -q "$PARENT.cam.r.${START_DATE}-00000.nc" "$REST_LOCAL/rpointer.atm" \
        || { echo "ERROR: rpointer.atm does not point to $START_DATE" >&2; exit 1; }
fi

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
cd "$NORESM_ROOT/cime/scripts"
./create_newcase --case "$CASEROOT" --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT
cd "$CASEROOT"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

if [[ "$COMPSET" == NF2000* ]]; then forcings_2000; else forcings_2100; fi
setup_nudging_data "$START_DATE"          # -offline_dyn + checks the met file of the start date exists
# Build-time flags the parent set through cases-setup.sh helpers (aerosol/cam diagnostics): copy them as they are
./xmlchange CAM_AEROCOM="$(./xmlquery --caseroot "$PARENT_CASEROOT" --value CAM_AEROCOM)"

if [[ $HYBRID -eq 1 ]]; then
    # Exactly the parent's start
    ./xmlchange RUN_TYPE=hybrid
    ./xmlchange RUN_REFCASE="$SPINUP"
    ./xmlchange RUN_REFDATE="$SPINUP_DATE"
    ./xmlchange RUN_STARTDATE=2000-01-01
else
    # Exact continuation of the parent from its own restart
    ./xmlchange RUN_TYPE=branch
    ./xmlchange RUN_REFCASE="$PARENT"
    ./xmlchange RUN_REFDATE="$START_DATE"
    ./xmlchange RUN_STARTDATE="$START_DATE"
fi
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

if [[ -n "$DAYS" ]]; then
    ./xmlchange STOP_OPTION=ndays,STOP_N=$DAYS,REST_OPTION=ndays,REST_N=$DAYS
    ./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=06:00:00
else
    # one model year per job (measured 6,828 core-hours per year → ≈ 13–14 h on 512 cores)
    ./xmlchange STOP_OPTION=nyears,STOP_N=1,REST_OPTION=nyears,REST_N=1
    ./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=30:00:00
fi
./xmlchange RESUBMIT=$([[ -n "$DAYS" ]] && echo "$NRESUB" || echo 0)
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE
./xmlchange --subgroup case.run        JOB_QUEUE=normal
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Namelists = the parent's, verbatim (no drift from later edits of cases-setup.sh)
for f in user_nl_cam user_nl_clm user_nl_cice user_nl_cpl user_nl_docn user_nl_mosart; do
    [[ -f "$PARENT_CASEROOT/$f" ]] && cp "$PARENT_CASEROOT/$f" "$f"
done
# A branch reads the restart directly: drop init interpolation (kept for the hybrid 2000 start, as in the parent)
[[ $HYBRID -eq 1 ]] || sed -i '/^ *use_init_interp *=/d' user_nl_clm
# Nudging: a branch starts the met reader from met_data_file: the file of the branch date (FIND_TIMES otherwise)
sed -i -E "s/(met_data_file *= *'.*\.cam\.h1\.)[0-9]{4}-01-01-00000\.nc'/\1${START_DATE}-00000.nc'/" user_nl_cam
grep -q "cam.h1.${START_DATE}-00000.nc'" user_nl_cam || { echo "ERROR: met_data_file not set to $START_DATE" >&2; exit 1; }
# From 2015 the met data are in the extended folder (MET run 2015-2025); the parents switch to it the same way
# (cases-setup.sh switch_case_to_met_2000_2025). The new folder's file list must reach the end of the chain year.
if (( YEAR >= 2015 )); then
    sed -i "/^ *met_\(data_file\|filenames_list\)/ s|_6h_2000-2015/|_6h_2000-2025/|" user_nl_cam
    METLIST=$(sed -n "s/^ *met_filenames_list *= *'\(.*\)'.*/\1/p" user_nl_cam)
    METFILE=$(sed -n "s/^ *met_data_file *= *'\(.*\)'.*/\1/p" user_nl_cam)
    [[ "$METLIST" == *_6h_2000-2025/* && -f "$METLIST" && -f "$METFILE" ]] \
        || { echo "ERROR: extended met folder not ready ($METLIST, $METFILE)" >&2; exit 1; }
    last=$(tail -n 1 "$METLIST" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tail -1)
    [[ ! "$last" < "$((YEAR + 1))-01-01" ]] || { echo "ERROR: met data end at $last, before $((YEAR + 1))-01-01" >&2; exit 1; }
fi

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
grep -Eq "^(fincl|mfilt|nhtfrq|avgflag_pertape)" user_nl_cam && { echo "ERROR: CAM history settings left" >&2; exit 1; }
grep -Eq "^hist_" user_nl_clm && { echo "ERROR: CLM history settings left" >&2; exit 1; }
grep -q "^empty_htapes *= *.true." user_nl_cam || { echo "ERROR: parent user_nl_cam has no empty_htapes = .true." >&2; exit 1; }

# CAM: only the MEGAN fluxes the atmosphere receives (monthly; 30-min for the identity check).
# Insert before the final "/" of the namelist group (the parent's file ends with it).
python3 - user_nl_cam <<'PYCAM'
import sys
p = sys.argv[1]; lines = open(p).read().rstrip("\n").split("\n")
assert lines[-1].strip() == "/", "user_nl_cam: last line is not '/'"
lines[-1:] = ["mfilt           = 1, 48", "nhtfrq          = 0, 1", "avgflag_pertape = 'A', 'I'",
              "fincl1 = 'SFISOP','SFMTERP'", "fincl2 = 'SFISOP','SFMTERP'", "/"]
open(p, "w").write("\n".join(lines) + "\n")
PYCAM

# CLM tape 1: monthly grid-cell MEGAN fields only; tape 2: per patch, every step, one file per day
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
cmp "$PARENT_CASEROOT/SourceMods/src.clm/VOCEmissionMod.F90" SourceMods/src.clm/VOCEmissionMod.F90 \
    || { echo "ERROR: CLM SourceMod differs from the parent's" >&2; exit 1; }

# Same model as the parent? Stop before building if not.
./preview_namelists > /dev/null
compare_xml_to_archived_case "$PARENT_CASEROOT"
compare_namelists_to_archived_case "$PARENT_CASEROOT/CaseDocs" "$ALLOWED_NML_KEYS"

cat > megan_lmdi_info.txt <<EOF
run=$RUN
parent=$PARENT
start_date=$START_DATE
mode=$([[ -n "$DAYS" ]] && echo "test $((NRESUB + 1)) jobs x ${DAYS} days" || echo "chain, 1 year per job")
created=$(date '+%Y-%m-%d %H:%M')
EOF

if [[ $CHECK_ONLY -eq 1 ]]; then echo "CHECK ONLY: comparisons passed, not built"; echo "CASE $CASENAME"; exit 0; fi
./case.build
echo "Built, not submitted. Submit with launch_megan_lmdi.sh."
echo "CASE $CASENAME"
