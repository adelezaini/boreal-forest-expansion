#!/bin/bash
# User 2026-11-11 12:25 (session d23b46ef): process LCC_FUT_fBVOClccFUT (24g) for 2001-2025 and switch the
# analysis from the design-B stand-in to the real run (design A): forcing_maps.LCC_FUT_FBVOCLCCFUT_DESIGN_B = False.
#
# Steps: 1 wait for the staging postprocessing ("All done.") -> 2 one retry of failed jobs, need 19 files
#        -> 3 2001-2014 slice of the new files = existing 24g 2001-2014 files -> 4 move into postprocessing/
#        -> 5 wait until no other analysis notebook run is active -> 6 snapshot results/{figures,tables}
#        -> 7 flag False (backup) -> 8 rerun the contrast notebooks (outputs saved) -> 9 SUMMARY.txt
# NOT rerun here: artefact-corrected-split + cumulative_radiative_decomposition (design B by construction,
# waiting for the user's decision on a design-A version).
# State/logs: /cluster/work/users/adelez/designA-24g/  (run.log, SUMMARY.txt, DONE or FAILED). Stop: touch STOP there.
set -u
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
STG=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing-24g-2001-2025-staging
DST=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
ST=/cluster/work/users/adelez/designA-24g
A=LCC_FUT_fBVOClccFUT
NBS="simulation-contrasts radiative_forcing bvoc-soa-cloud-interactions biogeophysical-hydro timeseries-responses
pd-fut-attribution fut-fbvoc-emission-source-choice land-carbon-water"
NPAR=4
SNAP=20261111
mkdir -p "$ST/backup"
log()  { echo "$(date '+%F %T') $*" >> "$ST/run.log"; }
fail() { log "ERROR: $*"; echo "$(date '+%F %T') $*" > "$ST/FAILED"; exit 1; }
stop() { [[ -f "$ST/STOP" ]] && { log "STOP file found, exiting"; exit 0; }; }
log "start on $(hostname), pid $$"

# 1. postprocessing done
until grep -q "^All done" "$STG/run_all.log" 2>/dev/null; do stop; sleep 300; done
log "postprocessing finished: OK $(grep -c '^OK' "$STG/run_all.log") FAILED $(grep -c '^FAILED' "$STG/run_all.log")"

# 2. one retry of failed jobs, 2 in parallel (AERSIZE was OOM-killed at 8 in parallel on 9 Nov)
if grep -q '^FAILED' "$STG/run_all.log"; then
    log "retrying failed jobs"
    (cd "$REPO/postprocess" && OUT_PATH="$STG" CASES="$(cat "$STG/cases.txt")" bash run_all_parallel.sh 2) > "$STG/run_all_retry.log" 2>&1
    log "retry: OK $(grep -c '^OK' "$STG/run_all_retry.log") FAILED $(grep -c '^FAILED' "$STG/run_all_retry.log")"
fi
n=$(ls "$STG"/${A}_*_2001-2025.nc 2>/dev/null | wc -l)
[[ $n -eq 19 ]] || fail "$n processed 2001-2025 files in staging (need 19); see $STG/run_all*.log"
log "19 files OK"

# 3. 2001-2014 slice = existing 2001-2014 files (fail > 1e-3 relative, warn > 1e-6), all 19 categories
"$PY" - "$STG" "$DST" "$A" >> "$ST/run.log" 2>&1 <<'EOF' || fail "2001-2014 consistency check failed (see run.log)"
import sys, glob, os, numpy as np, xarray as xr
stg, dst, a = sys.argv[1:]
bad = 0
for f in sorted(glob.glob(f"{stg}/{a}_*_2001-2025.nc")):
    old_f = f"{dst}/{os.path.basename(f).replace('2001-2025', '2001-2014')}"
    new = xr.open_dataset(f)
    if new.sizes["time"] != 300:
        print(f"  TIME {f} {new.sizes['time']}"); bad += 1; continue
    if not os.path.exists(old_f):
        print(f"  no 2001-2014 file for {os.path.basename(f)}: time check only"); continue
    old = xr.open_dataset(old_f)
    sl = new.sel(time=new["time"].dt.year <= 2014)
    worst = 0.0
    for v in old.data_vars:
        if v not in sl or "time" not in old[v].dims or not np.issubdtype(old[v].dtype, np.number):
            continue
        x, y = sl[v].values, old[v].values
        if x.shape != y.shape:
            print(f"  SHAPE {v} {x.shape} vs {y.shape}"); bad += 1; continue
        scale = np.nanmax(np.abs(y)) or 1.0
        d = np.nanmax(np.abs(x - y)) / scale if np.isfinite(x).any() else 0.0
        worst = max(worst, d)
        if d > 1e-3:
            print(f"  DIFF {os.path.basename(f)} {v} rel {d:.2e}"); bad += 1
    print(f"check {os.path.basename(f)}: max rel diff {worst:.1e}" + ("  (WARN > 1e-6)" if worst > 1e-6 else ""))
sys.exit(1 if bad else 0)
EOF
log "consistency check passed"

# 4. move into the analysis folder (2001-2014 files stay)
for f in "$STG"/${A}_*_2001-2025.nc; do [[ -e "$DST/$(basename "$f")" ]] && fail "exists already: $DST/$(basename "$f")"; done
mv "$STG"/${A}_*_2001-2025.nc "$DST"/ || fail "mv to $DST failed"
mkdir -p "$DST/logs_2001-2025" && cp -p "$STG"/logs/*.log "$DST/logs_2001-2025/"
log "moved 19 files to $DST"

# 5. wait for other analysis notebook runs
while pgrep -f "run_nb_inplace.py analysis/" > /dev/null; do stop; log "waiting: other analysis notebook run active"; sleep 600; done

# 6. snapshot current (design-B stand-in) results
cd "$REPO" || fail "cd $REPO"
for d in figures tables; do
    S="results/${d}-designB-standin-$SNAP"
    [[ -e "$S" ]] && fail "$S exists already"
    cp -a "results/$d" "$S" || fail "snapshot $d"
    [[ $(find "results/$d" -type f | wc -l) -eq $(find "$S" -type f | wc -l) ]] || fail "snapshot $d: file count differs"
done
log "snapshot -> results/{figures,tables}-designB-standin-$SNAP"

# 7. flag -> False
FM=src/boreal_forest_expansion/plotting/forcing_maps.py
cp -p "$FM" "$ST/backup/"
for nb in $NBS; do cp -p "analysis/$nb.ipynb" "$ST/backup/"; done
grep -q "^LCC_FUT_FBVOCLCCFUT_DESIGN_B = True" "$FM" || fail "flag line not found in $FM"
sed -i 's/^LCC_FUT_FBVOCLCCFUT_DESIGN_B = True.*/LCC_FUT_FBVOCLCCFUT_DESIGN_B = False   # user 2026-11-11: real 24g run (design A), 2001-2025 processed/' "$FM"
"$PY" -c "import sys; sys.path.insert(0,'src'); import boreal_forest_expansion.plotting.forcing_maps as fm; assert fm.LCC_FUT_FBVOCLCCFUT == 'LCC_FUT_fBVOClccFUT'; assert not any(c.design_b for r in fm.CONTRASTS.values() for c in r)" \
    >> "$ST/run.log" 2>&1 || fail "flag switch check failed"
log "forcing_maps: LCC_FUT_FBVOCLCCFUT_DESIGN_B = False (no design-B contrast left)"

# 8. run
run_nb() {
    nb=$1; L="results/tables/logs/run_${nb}_designA_20261111.log"; t0=$(date +%s)
    "$PY" results/tables/logs/run_nb_inplace.py "analysis/$nb.ipynb" --timeout 21600 > "$L" 2>&1; rc=$?
    echo "$(date '+%F %T') $nb EXIT $rc ($(( ($(date +%s) - t0) / 60 )) min) log $L"
}
export -f run_nb; export PY
log "running $NPAR in parallel: $(echo $NBS)"
echo $NBS | tr ' ' '\n' | xargs -P $NPAR -I{} bash -c 'run_nb {}' >> "$ST/run.log" 2>&1

# 9. summary
{
    echo "design-A switch (session d23b46ef script), finished $(date '+%F %T')"
    grep -E ' EXIT [0-9]+ ' "$ST/run.log"
    echo "figures newer than the flag switch: $(find results/figures -name '*.png' -newer "$ST/backup/forcing_maps.py" | wc -l)"
    echo "stale design-B files left in results/figures (name contains 'design B'): $(find results/figures results/tables -name '*design B*' | wc -l)"
    echo "NOT rerun: artefact-corrected-split, cumulative_radiative_decomposition (design B by construction)."
} > "$ST/SUMMARY.txt"
cat "$ST/SUMMARY.txt" >> "$ST/run.log"
if grep -qE ' EXIT [1-9]' "$ST/run.log"; then echo "some notebooks failed, see SUMMARY.txt" > "$ST/FAILED"; else touch "$ST/DONE"; fi
log "end"
