#!/bin/bash
# Launch the new (20261025) spin-up chain automatically, as each step finishes (user 2026-10-25):
#   A: 12c land-only CTRL PD done -> NIRD copy -> 13c (coupled CTRL PD) -> done -> NIRD copy -> 13a (CTRL_PD nudged)
#   B: 13b coupled LCC PD done    -> NIRD copy -> 14a (LCC_PD nudged)
#   C: 23c coupled CTRL FUT done  -> NIRD copy -> 23a (CTRL_FUT nudged)
#   D: 23b coupled LCC FUT done   -> NIRD copy -> 24a (LCC_FUT nudged)
# Before a nudged run is launched its REFCASE is set to the new coupled spin-up (REFDATE stays 0021-01-01).
# "Done" = no Slurm job left for the case, RESUBMIT=0, last CaseStatus st_archive entry = success,
# and the final restart folder in the archive. A case that stops without that -> FAILED, branch halted.
# Idempotent (state in $STATE): safe to restart after a login-node reboot:
#   nohup setsid bash auto_launch_new_chain.sh >> /cluster/work/users/adelez/auto-launch/watcher.out 2>&1 &
# Stop: touch /cluster/work/users/adelez/auto-launch/STOP
set -uo pipefail

SCRIPTS=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/cases-scripts
CASES=$(realpath /cluster/home/adelez/cases/BRL_FRST_XPSN)  # = /cluster/projects/..., as squeue %Z reports it
ARCHIVE=/cluster/work/users/adelez/archive
NIRD=/cluster/home/adelez/nird/BRL-FRST-XPSN_archive
STATE=/cluster/work/users/adelez/auto-launch
POLL=900
mkdir -p "$STATE"

log() { echo "$(date '+%F %T') $*" | tee -a "$STATE/launch.log"; }

case_status() {  # prints RUNNING | DONE | FAILED for case $1 with final restart date $2
    local c=$1 refdate=$2 root="$CASES/$1"
    [[ -d "$root" ]] || { echo FAILED; return; }
    if squeue -h -u "$USER" -o "%Z" | grep -qx "$root"; then echo RUNNING; return; fi
    local resub last
    resub=$(cd "$root" && ./xmlquery RESUBMIT --value 2>/dev/null)
    last=$(grep "st_archive" "$root/CaseStatus" | tail -1)
    if [[ "$resub" == 0 && "$last" == *"st_archive success"* ]] && ls "$ARCHIVE/$c/rest/$refdate-00000/"*.r.* >/dev/null 2>&1; then
        echo DONE
    else
        echo FAILED
    fi
}

to_nird() {  # same rsync as save-archived-case-to-boreal (~/.bashrc)
    rsync -ah --exclude='*_tmp.pid*.ncks.tmp' "$ARCHIVE/$1/" "$NIRD/$1/" >> "$STATE/rsync_$1.log" 2>&1
}

set_refcase() {  # set REFCASE in script $1 to $2, check the edit
    local f; f=$(ls "$SCRIPTS"/$1-*.sh)
    sed -i "s|^REFCASE=.*|REFCASE=\"$2\"|" "$f"
    grep -qx "REFCASE=\"$2\"" "$f" && grep -qx 'REFDATE="0021-01-01"' "$f"
}

launch() {  # run case script $1, stdin "n" so an unexpected case-removal prompt aborts instead of hanging
    log "launching $1"
    (cd "$SCRIPTS" && echo n | bash "$(ls $1-*.sh)") > "$STATE/launch_$1.log" 2>&1
    local rc=$?; log "$1 script exit $rc (log $STATE/launch_$1.log)"; return $rc
}

# step NAME SRC_CASE SRC_REFDATE ACTION...: run ACTION once SRC_CASE is DONE (state file = NAME)
step() {
    local name=$1 src=$2 refdate=$3; shift 3
    [[ -e "$STATE/$name.done" || -e "$STATE/$name.failed" ]] && return
    local st; st=$(case_status "$src" "$refdate")
    [[ $st == RUNNING ]] && return
    if [[ $st == FAILED ]]; then log "FAILED: $src stopped before finishing -> $name halted"; touch "$STATE/$name.failed"; return; fi
    log "$src DONE -> NIRD copy"
    to_nird "$src" || { log "rsync $src failed"; touch "$STATE/$name.failed"; return; }
    if "$@"; then touch "$STATE/$name.done"; else log "$name failed"; touch "$STATE/$name.failed"; fi
}

new_case() { ls -td "$CASES"/$1-2026* 2>/dev/null | head -1 | xargs -r basename; }

do_13c()  { launch 13c && new_case NF2000norbc_tropstratchem_spinup_ctrl_f19_f19 > "$STATE/13c.case"; }
do_13a()  { set_refcase 13a "$(cat "$STATE/13c.case")" && launch 13a; }
do_14a()  { set_refcase 14a NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025 && launch 14a; }
do_23a()  { set_refcase 23a NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025 && launch 23a; }
do_24a()  { set_refcase 24a NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025 && launch 24a; }

if [[ ${1:-} == --check ]]; then  # print the status of the watched cases and exit
    for c in I2000Clm50BgcCropCplHist_ctrl_f19_f19-20261025:0101-01-01 \
             NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025:0021-01-01 \
             NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025:0021-01-01 \
             NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025:0021-01-01; do
        echo "${c%%:*} $(case_status "${c%%:*}" "${c##*:}")"
    done
    [[ -s "$STATE/13c.case" ]] && echo "$(cat "$STATE/13c.case") $(case_status "$(cat "$STATE/13c.case")" 0021-01-01)"
    ls "$STATE"/*.done "$STATE"/*.failed 2>/dev/null
    exit 0
fi

log "watcher started on $(hostname), pid $$"
while [[ ! -e "$STATE/STOP" ]]; do
    step 13c I2000Clm50BgcCropCplHist_ctrl_f19_f19-20261025 0101-01-01 do_13c
    [[ -e "$STATE/13c.done" ]] && step 13a "$(cat "$STATE/13c.case")" 0021-01-01 do_13a
    step 14a NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025 0021-01-01 do_14a
    step 23a NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025 0021-01-01 do_23a
    step 24a NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025 0021-01-01 do_24a
    n=$(ls "$STATE"/{13a,14a,23a,24a}.{done,failed} 2>/dev/null | wc -l)
    [[ $n -ge 4 ]] && { log "all branches finished"; break; }
    sleep $POLL
done
log "watcher exit"
