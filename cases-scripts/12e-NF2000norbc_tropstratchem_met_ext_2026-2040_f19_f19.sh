#!/bin/bash

### MET continuation 2026-01-01 -> 2041-01-02 (user 2026-11-11, plan approved 2026-11-15)
# NO NEW CASE: MET = NF2000norbc_tropstratchem_met_f19_f19_20260422 (12a 2000-2014, 12d 2015-2025)
# simply continues in place (CONTINUE_RUN=TRUE, its run dir points to the 2026-01-01 restart),
# like any resubmission. This script only checks, backs up, changes the stop settings and submits.
#   3 jobs of 6 yr: 2026->2032, 2032->2038, 2038->2041-01-02 (cut by STOP_DATE: 1 day past 2041 so the
#   met files have records after the nudged runs' last time step 2041-01-01 00 h). 6 yr, not 5:
#   STOP_DATE only shortens a job, so 3 x 5 yr would end at 2041-01-01 (same trick as 12d).
#   ~6.8 simulated yr/day -> ~21 h per job (wallclock 48:59).
# Record: docs/met-nudg-2026-2040.md. The watcher run_when_done/met_nudg_2026-2040_when_done.sh
# builds the nudging days after each archived job and runs the gate after job 1.
#
# Usage (from cases-scripts/):
#   bash 12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh --check   checks only, changes nothing
#   bash 12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh           checks, backups, xmlchange, case.submit
#   bash 12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh --gate    after job 1: the new h1 2026-01-01-21600 must be
#                                                value-identical to the original (moved) one
#                                                (PS U V T Q time date datesec, all records). Exit 0 = OK.

set -euo pipefail
MODE="${1:-run}"
MET=NF2000norbc_tropstratchem_met_f19_f19_20260422
CASEROOT=$HOME/cases/BRL_FRST_XPSN/$MET
ARCH=/cluster/work/users/$USER/archive/$MET
KEEP=$ARCH/pre-2026-2040-continuation          # original 2026-01 history files of the 2015-2025 job
H1=$MET.cam.h1.2026-01-01-21600.nc
EXCLUDE="--exclude=b[5101,5103-5196,5203-5204,5207-5296]"
STATE=/cluster/work/users/$USER/met-nudg-2040
mkdir -p "$STATE"
log() { echo "$(date '+%F %T') $*" | tee -a "$STATE/12e.log"; }

if [[ "$MODE" == "--gate" ]]; then
    [[ -f "$KEEP/atm/hist/$H1" && -f "$ARCH/atm/hist/$H1" ]] || { echo "ERROR: missing $H1 (original or new)" >&2; exit 1; }
    python3 - "$KEEP/atm/hist/$H1" "$ARCH/atm/hist/$H1" <<'EOF'
import sys, netCDF4, numpy as np
o, n = netCDF4.Dataset(sys.argv[1]), netCDF4.Dataset(sys.argv[2])
bad = [v for v in ["time", "date", "datesec", "PS", "U", "V", "T", "Q"]
       if o[v].shape != n[v].shape or not np.array_equal(o[v][:], n[v][:])]
print(f"gate: {sys.argv[2]} vs original: " + ("IDENTICAL (PS U V T Q time date datesec)" if not bad else f"DIFFERS in {bad}"))
sys.exit(1 if bad else 0)
EOF
    exit $?
fi
[[ "$MODE" == run || "$MODE" == --check ]] || { echo "Usage: $0 [--check|--gate]" >&2; exit 1; }

cd "$CASEROOT"
RUNDIR=$(./xmlquery --value RUNDIR)
# 1. checks
squeue -u "$USER" -h -o %Z | grep -qx -- "$(realpath "$CASEROOT")" && { echo "ERROR: a MET job is queued" >&2; exit 1; }
[[ $(./xmlquery --value CONTINUE_RUN) == TRUE ]] || { echo "ERROR: CONTINUE_RUN is not TRUE" >&2; exit 1; }
grep -q "$MET.cam.r.2026-01-01-00000.nc" "$RUNDIR/rpointer.atm" || { echo "ERROR: rpointer.atm not at 2026-01-01" >&2; exit 1; }
for c in cam.r cam.rs clm2.r cpl.r cice.r mosart.r; do
    [[ -f "$RUNDIR/$MET.$c.2026-01-01-00000.nc" ]] || { echo "ERROR: missing run-dir restart $c" >&2; exit 1; }
done
[[ -f "$RUNDIR/$MET.docn.rs1.2026-01-01-00000.bin" ]] || { echo "ERROR: missing docn restart" >&2; exit 1; }
[[ -f "$RUNDIR/$MET.cam.h1.2025-12-31-21600.nc" ]] || { echo "ERROR: missing open h1 file 2025-12-31-21600 in the run dir" >&2; exit 1; }
tail -n 3 CaseStatus | grep -q 'st_archive success' || { echo "ERROR: last CaseStatus entry is not st_archive success" >&2; exit 1; }
mapfile -t MOVE < <(cd "$ARCH" && find . -path '*/hist/*' -name "$MET.*.2026-*" | sort)
echo "archived 2026 history files to move: ${MOVE[*]:-none}"
[[ -f "$KEEP/atm/hist/$H1" || " ${MOVE[*]} " == *"/$H1 "* ]] || { echo "ERROR: original $H1 not found (needed for the gate)" >&2; exit 1; }
echo "now: STOP_OPTION=$(./xmlquery --value STOP_OPTION) STOP_N=$(./xmlquery --value STOP_N) STOP_DATE=$(./xmlquery --value STOP_DATE) RESUBMIT=$(./xmlquery --value RESUBMIT) wallclock=$(./xmlquery --value JOB_WALLCLOCK_TIME --subgroup case.run)"
echo "submit options: $(grep batch_args .submit_options 2>/dev/null || echo none)"
if [[ "$MODE" == --check ]]; then echo "CHECK OK: MET can continue 2026-01-01 -> 2041-01-02"; exit 0; fi

# 2. backups + move the old 2026 history files out of the archive's way
[[ -f env_run.xml.before_2026-2040 ]] || cp -p env_run.xml env_run.xml.before_2026-2040
[[ -f .submit_options.before_2026-2040 ]] || cp -p .submit_options .submit_options.before_2026-2040
for f in "${MOVE[@]}"; do
    mkdir -p "$KEEP/$(dirname "$f")"
    mv -n "$ARCH/$f" "$KEEP/$f"
    log "moved archive $f -> pre-2026-2040-continuation/"
done

# 3. stop settings (REST yearly and wallclock 48:59 unchanged) + full bad-node exclude list
./xmlchange STOP_OPTION=nyears,STOP_N=6,STOP_DATE=20410102,RESUBMIT=2
./xmlchange REST_OPTION=nyears,REST_N=1
log "xmlchange STOP_OPTION=nyears STOP_N=6 STOP_DATE=20410102 RESUBMIT=2"

# 4. submit (--batch-args is stored in .submit_options, so it also applies to resubmits and st_archive)
./case.submit --batch-args="$EXCLUDE" 2>&1 | tee "$STATE/12e_submit.log"
log "MET submitted: $(grep -oE 'Submitted job [^ ]+ with id [0-9]+' "$STATE/12e_submit.log" | tr '\n' ';')"
date '+%F %T' > "$STATE/met.submitted"
