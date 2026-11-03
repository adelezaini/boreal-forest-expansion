#!/bin/bash
# Launch the new (20261025) spin-up chain automatically, as each step finishes (user 2026-10-25):
#   A: 12c land-only CTRL PD done -> NIRD copy -> 13c (coupled CTRL PD) -> done -> NIRD copy -> 13a (CTRL_PD nudged)
#   B: 13b coupled LCC PD done    -> NIRD copy -> 14a (LCC_PD nudged)
#   C: 23c coupled CTRL FUT done  -> NIRD copy -> 23a (CTRL_FUT nudged)
#   D: 23b coupled LCC FUT done   -> NIRD copy -> 24a (LCC_FUT nudged)
# Before a nudged run is launched its REFCASE is set to the new coupled spin-up (REFDATE stays 0021-01-01).
# fBVOC on the new chain (user 2026-10-28): nudged source run done (rest 2015-01-01) -> NIRD copy
#   -> 19-species climatology 2001-2014 (sbatch run_bvoc_climatology_array.sh) -> check_bvoc_climatology.py
#   -> relabel to 2100 -> set REFCASE (LCC spin-up) + EMS_PREFIX / LCC_PD_CASE -> launch:
#   E: 13a CTRL_PD  -> 14b LCC_PD_fBVOCctrlPD, 24b LCC_FUT_fBVOCctrlPD, 14c CTRL_PD_fBVOCctrlPD (user 2026-10-29)
#   F: 23a CTRL_FUT -> 24c LCC_FUT_fBVOCctrlFUT, 24e CTRL_FUT_fBVOCctrlFUT (user 2026-10-30)
#   G: 14a LCC_PD   -> 24d LCC_FUT_fBVOClccPD, 14e LCC_PD_fBVOClccPD (3 yr, 2000-2002; user 2026-10-30)
# Postprocessing (user 2026-10-29): every nudged run of the chain (13a 14a 23a 24a 14b 14c 14e 24b 24c 24d 24e), once DONE
#   (rest 2015-01-01; 14e: 2003-01-01) -> NIRD copy -> background postprocess/postprocess_new_chain_run.sh <alias> <case> (one at a time):
#   old <alias> files moved to the archive folders, then all atm + lnd categories. State pp<n>.{done,failed} = started,
#   pp<n>.{ok,err,log} = result.
#   State: <src>.case (launched case name), clim<src>.{done,failed} + clim<src>.job (array id),
#   ems<src>.{done,failed} (array finished + check + relabel), check_<src>.log, <fBVOC>.{done,failed}.
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
BVOC=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/preprocess/bvoc-emissions
EMS_DIR=/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
LCC_PD_SPIN=NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025
LCC_FUT_SPIN=NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025
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
do_13a()  { set_refcase 13a "$(cat "$STATE/13c.case")" && launch 13a && new_case NF2000norbc_tropstratchem_nudg_ctrl_f19_f19 > "$STATE/13a.case"; }
do_14a()  { set_refcase 14a $LCC_PD_SPIN && launch 14a && new_case NF2000norbc_tropstratchem_nudg_lcc_f19_f19 > "$STATE/14a.case"; }
do_23a()  { set_refcase 23a NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025 && launch 23a && new_case NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19 > "$STATE/23a.case"; }
do_24a()  { set_refcase 24a $LCC_FUT_SPIN && launch 24a && new_case NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19 > "$STATE/24a.case"; }

# --- fBVOC on the new chain ---
set_var() {  # set VAR="value" (whole line) in script $1, check the edit; refuses an empty value
    [[ -n $3 ]] || return 1
    local f; f=$(ls "$SCRIPTS"/$1-*.sh)
    sed -i "s|^$2=.*|$2=\"$3\"|" "$f"
    grep -qx "$2=\"$3\"" "$f"
}

do_clim() {  # submit the 19-species climatology array for source run $1 (13a|14a|23a)
    local c jid; c=$(cat "$STATE/$1.case")
    jid=$(cd "$BVOC" && sbatch --parsable run_bvoc_climatology_array.sh "$c" 2001 2014) || return 1
    echo "$jid" > "$STATE/clim$1.job"; log "climatology $c: array $jid"
}

ems_step() {  # ems$1: once the climatology array of source $1 has finished, check it and relabel to 2100
    local src=$1 name=ems$1
    [[ -e "$STATE/$name.done" || -e "$STATE/$name.failed" ]] && return
    [[ -e "$STATE/clim$src.failed" ]] && { log "FAILED: clim$src -> $name halted"; touch "$STATE/$name.failed"; return; }
    [[ -e "$STATE/clim$src.done" ]] || return
    local jid c states; jid=$(cat "$STATE/clim$src.job"); c=$(cat "$STATE/$src.case")
    [[ -n $(squeue -h -j "$jid" 2>/dev/null) ]] && return
    states=$(sacct -n -X -j "$jid" -o State | sort -u | xargs)
    [[ -z $states ]] && return  # sacct not updated yet
    if [[ $states != COMPLETED ]]; then log "FAILED: climatology array $jid ($states) -> $name halted"; touch "$STATE/$name.failed"; return; fi
    log "climatology $c done -> check + relabel to 2100"
    if (cd "$BVOC" && "$PY" check_bvoc_climatology.py "$c" 2001 2014 && bash create_bvoc_emissions_for_year_2100.sh "${c}_2001-2014") \
            >> "$STATE/check_$src.log" 2>&1; then
        touch "$STATE/$name.done"
    else
        log "FAILED: check/relabel of $c (log $STATE/check_$src.log) -> $name halted"; touch "$STATE/$name.failed"
    fi
}

# after NAME DEP ACTION...: run ACTION once DEP.done exists (a failed DEP fails NAME)
after() {
    local name=$1 dep=$2; shift 2
    [[ -e "$STATE/$name.done" || -e "$STATE/$name.failed" ]] && return
    [[ -e "$STATE/$dep.failed" ]] && { log "FAILED: $dep -> $name halted"; touch "$STATE/$name.failed"; return; }
    [[ -e "$STATE/$dep.done" ]] || return
    if "$@"; then touch "$STATE/$name.done"; else log "$name failed"; touch "$STATE/$name.failed"; fi
}

ems() { echo "$EMS_DIR/ems_$(cat "$STATE/$1.case")_2001-2014${2:-}"; }  # EMS_PREFIX of source $1, suffix $2
do_14b() { set_refcase 14b $LCC_PD_SPIN  && set_var 14b EMS_PREFIX "$(ems 13a)" && launch 14b && new_case NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19 > "$STATE/14b.case"; }
do_14c() { set_refcase 14c "$(cat "$STATE/13c.case")" && set_var 14c EMS_PREFIX "$(ems 13a)" && launch 14c && new_case NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19 > "$STATE/14c.case"; }
do_24b() { set_refcase 24b $LCC_FUT_SPIN && set_var 24b EMS_PREFIX "$(ems 13a _on_yr2100)" && launch 24b && new_case NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19 > "$STATE/24b.case"; }
do_24c() { set_refcase 24c $LCC_FUT_SPIN && set_var 24c EMS_PREFIX "$(ems 23a _on_yr2100)" && launch 24c && new_case NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19 > "$STATE/24c.case"; }
do_14e() { set_refcase 14e $LCC_PD_SPIN  && set_var 14e EMS_PREFIX "$(ems 14a)" && launch 14e && new_case NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19 > "$STATE/14e.case"; }
do_24e() { set_refcase 24e NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025 && set_var 24e EMS_PREFIX "$(ems 23a _on_yr2100)" && launch 24e && new_case NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19 > "$STATE/24e.case"; }
do_24d() { set_refcase 24d $LCC_FUT_SPIN && set_var 24d LCC_PD_CASE "$(cat "$STATE/14a.case")" && launch 24d && new_case NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19 > "$STATE/24d.case"; }

# a source run's step: once done (rest 2015-01-01) -> NIRD copy -> climatology array
src_step() {
    if [[ -e "$STATE/$1.failed" && ! -e "$STATE/clim$1.failed" ]]; then log "FAILED: $1 -> clim$1 halted"; touch "$STATE/clim$1.failed"; fi
    [[ -s "$STATE/$1.case" ]] && step clim$1 "$(cat "$STATE/$1.case")" 2015-01-01 do_clim $1
}

# --- postprocessing of finished runs ---
PP=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/postprocess/postprocess_new_chain_run.sh
declare -A ALIAS=([13a]=CTRL_PD [14a]=LCC_PD [23a]=CTRL_FUT [24a]=LCC_FUT [14b]=LCC_PD_fBVOCctrlPD [14c]=CTRL_PD_fBVOCctrlPD
                  [24b]=LCC_FUT_fBVOCctrlPD [24c]=LCC_FUT_fBVOCctrlFUT [24d]=LCC_FUT_fBVOClccPD
                  [14e]=LCC_PD_fBVOClccPD [24e]=CTRL_FUT_fBVOCctrlFUT)
declare -A FINAL=([14e]=2003-01-01)  # final restart date if not 2015-01-01 (short runs)
do_pp() {  # start the postprocessing of run $1 in the background (it waits for its turn on a lock)
    log "postprocess ${ALIAS[$1]} $(cat "$STATE/$1.case") (log $STATE/pp$1.log)"
    nohup setsid bash "$PP" "${ALIAS[$1]}" "$(cat "$STATE/$1.case")" "$STATE/pp$1" < /dev/null > /dev/null 2>&1 &
}
pp_branch() {  # pp$1 once run $1 (launched, case name in $1.case) is DONE; a failed launch fails pp$1
    local name=pp$1
    [[ -e "$STATE/$name.done" || -e "$STATE/$name.failed" ]] && return
    [[ -e "$STATE/$1.failed" ]] && { log "FAILED: $1 -> $name halted"; touch "$STATE/$name.failed"; return; }
    [[ -e "$STATE/$1.done" && -s "$STATE/$1.case" ]] && step $name "$(cat "$STATE/$1.case")" "${FINAL[$1]:-2015-01-01}" do_pp $1
}

if [[ ${1:-} == --check ]]; then  # print the status of the watched cases and exit
    for c in I2000Clm50BgcCropCplHist_ctrl_f19_f19-20261025:0101-01-01 \
             NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025:0021-01-01 \
             NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19-20261025:0021-01-01 \
             NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-20261025:0021-01-01; do
        echo "${c%%:*} $(case_status "${c%%:*}" "${c##*:}")"
    done
    [[ -s "$STATE/13c.case" ]] && echo "$(cat "$STATE/13c.case") $(case_status "$(cat "$STATE/13c.case")" 0021-01-01)"
    for s in 13a 14a 23a; do [[ -s "$STATE/$s.case" ]] && echo "$(cat "$STATE/$s.case") $(case_status "$(cat "$STATE/$s.case")" 2015-01-01)"; done
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
    for s in 13a 14a 23a; do src_step $s; ems_step $s; done
    after 14b ems13a do_14b
    after 14c ems13a do_14c
    after 24b ems13a do_24b
    after 24c ems23a do_24c
    after 24d ems14a do_24d
    after 24e ems23a do_24e
    after 14e ems14a do_14e
    for r in 13a 14a 23a 24a 14b 14c 14e 24b 24c 24d 24e; do pp_branch $r; done
    # failures propagate (clim -> ems -> fBVOC), so every branch ends in a .done or .failed
    n=$(ls "$STATE"/pp{13a,14a,23a,24a,14b,14c,14e,24b,24c,24d,24e}.{done,failed} 2>/dev/null | wc -l)
    [[ $n -ge 11 ]] && { log "all branches finished"; break; }
    sleep $POLL
done
log "watcher exit"
