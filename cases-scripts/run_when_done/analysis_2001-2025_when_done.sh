#!/bin/bash
# User 2026-11-08 22:58 (session 4f89c2b2): once the 2001-2025 postprocessing of the 11 nudged runs is done,
# switch the analysis notebooks to 2001-2025 (early 2001-2014 / late 2015-2025) and run them, ready for the
# presentation on Mon 9 Nov morning. LCC_FUT_fBVOClccFUT: design-B stand-in (already in the notebooks/forcing_maps).
#
# Steps: 1 wait for postprocessing (staging run_all.log "ALL DONE") -> 2 one retry of failed jobs, need 209 files
#        -> 3 check the 2001-2014 slice of new files against the existing 2001-2014 files -> 4 move new files into
#        data/processed-data/postprocessing/ (2001-2014 files kept) -> 5 wait until no other analysis notebook run
#        is active (session 2e8818ca reorg) -> 6 patch START/END_YEAR in the notebooks + EARLY/LATE_YEARS in
#        forcing_maps.py (backups in $ST/backup) -> 7 run the notebooks (5 in parallel, outputs saved) -> 8 SUMMARY.txt
# State/logs: /cluster/work/users/adelez/analysis-2001-2025/  (run.log, SUMMARY.txt, DONE or FAILED)
# Stop: touch /cluster/work/users/adelez/analysis-2001-2025/STOP
set -u
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
STG=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing-2001-2025-staging
DST=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
ST=/cluster/work/users/adelez/analysis-2001-2025
NBS="radiative_forcing bvoc-soa-cloud-interactions biogeophysical-hydro simulation-contrasts timeseries-responses
pd-fut-attribution fut-fbvoc-emission-source-choice artefact-corrected-split cumulative_radiative_decomposition"
NPAR=5
mkdir -p "$ST/backup"
log()  { echo "$(date '+%F %T') $*" >> "$ST/run.log"; }
fail() { log "ERROR: $*"; echo "$(date '+%F %T') $*" > "$ST/FAILED"; exit 1; }
stop() { [[ -f "$ST/STOP" ]] && { log "STOP file found, exiting"; exit 0; }; }
log "start on $(hostname), pid $$"

# 1. postprocessing done
until grep -q "ALL DONE" "$STG/run_all.log" 2>/dev/null; do stop; sleep 300; done
log "postprocessing finished: OK $(grep -c '^OK' "$STG/run_all.log") FAILED $(grep -c '^FAILED' "$STG/run_all.log")"

# 2. one retry of failed jobs (run_all_parallel skips outputs that exist)
if grep -q '^FAILED' "$STG/run_all.log"; then
    log "retrying failed jobs"
    (cd "$REPO/postprocess" && OUT_PATH="$STG" CASES="$(cat "$STG/cases.txt")" bash run_all_parallel.sh 8) > "$STG/run_all_retry.log" 2>&1
    log "retry: OK $(grep -c '^OK' "$STG/run_all_retry.log") FAILED $(grep -c '^FAILED' "$STG/run_all_retry.log")"
fi
n=$(ls "$STG"/*_2001-2025.nc 2>/dev/null | wc -l)
[[ $n -eq 209 ]] || fail "$n processed 2001-2025 files in staging (need 209 = 11 x 19); see $STG/run_all*.log"
log "209 files OK"

# 3. 2001-2014 slice of the new files = existing 2001-2014 files (fail > 1e-3 relative, warn > 1e-6)
"$PY" - "$STG" "$DST" >> "$ST/run.log" 2>&1 <<'EOF' || fail "2001-2014 consistency check failed (see run.log)"
import sys, numpy as np, xarray as xr
stg, dst = sys.argv[1:]
checks = [("CTRL_PD", "atm", "RADIATIVE"), ("LCC_FUT_fBVOCctrlFUT", "atm", "SOA"), ("LCC_PD", "lnd", "BVOC"),
          ("CTRL_FUT_fBVOCctrlFUT", "lnd", "HYDRO"), ("LCC_PD_fBVOClccPD", "atm", "CLOUDPROP")]
bad = 0
for a, comp, cat in checks:
    new = xr.open_dataset(f"{stg}/{a}_{comp}_{cat}_2001-2025.nc")
    old = xr.open_dataset(f"{dst}/{a}_{comp}_{cat}_2001-2014.nc")
    assert new.sizes["time"] == 300, (a, cat, new.sizes["time"])
    sl = new.sel(time=new["time"].dt.year <= 2014)
    worst = 0.0
    for v in old.data_vars:
        if v not in sl or "time" not in old[v].dims or not np.issubdtype(old[v].dtype, np.number):
            continue
        x, y = sl[v].values, old[v].values
        if x.shape != y.shape:
            print(f"  SHAPE {a} {cat} {v} {x.shape} vs {y.shape}"); bad += 1; continue
        scale = np.nanmax(np.abs(y)) or 1.0
        d = np.nanmax(np.abs(x - y)) / scale if np.isfinite(x).any() else 0.0
        worst = max(worst, d)
        if d > 1e-3:
            print(f"  DIFF {a} {cat} {v} rel {d:.2e}"); bad += 1
    print(f"check {a} {comp} {cat}: max rel diff {worst:.1e}" + ("  (WARN > 1e-6)" if worst > 1e-6 else ""))
sys.exit(1 if bad else 0)
EOF
log "consistency check passed"

# 4. move into the analysis folder (2001-2014 files stay)
for f in "$STG"/*_2001-2025.nc; do [[ -e "$DST/$(basename "$f")" ]] && fail "exists already: $DST/$(basename "$f")"; done
mv "$STG"/*_2001-2025.nc "$DST"/ || fail "mv to $DST failed"
mkdir -p "$DST/logs_2001-2025" && cp -p "$STG"/logs/*.log "$STG"/run_all*.log "$DST/logs_2001-2025/"
log "moved 209 files to $DST (logs in logs_2001-2025/)"

# 5. wait for other analysis notebook runs (session 2e8818ca reorg reruns)
while pgrep -f "run_nb_inplace.py analysis/" > /dev/null; do stop; log "waiting: other analysis notebook run active ($(pgrep -fa 'run_nb_inplace.py analysis/' | grep -o 'analysis/[^ ]*' | sort -u | tr '\n' ' '))"; sleep 600; done
log "no other analysis notebook run active"

# 6. patch years (at run time, so the other session's latest notebook versions are used)
cd "$REPO" || fail "cd $REPO"
for nb in $NBS; do cp -p "analysis/$nb.ipynb" "$ST/backup/"; done
cp -p src/boreal_forest_expansion/plotting/forcing_maps.py "$ST/backup/"
"$PY" - $NBS >> "$ST/run.log" 2>&1 <<'EOF' || fail "patching failed (see run.log; backups in $ST/backup)"
import json, re, sys
from pathlib import Path
fm = Path("src/boreal_forest_expansion/plotting/forcing_maps.py")
s = fm.read_text()
old = "EARLY_YEARS, LATE_YEARS = (2001, 2007), (2008, 2014)"
new = ("EARLY_YEARS, LATE_YEARS = (2001, 2014), (2015, 2025)   # user 2026-11-08: early = fBVOC climatology years, "
       "late = years outside it (was 2001-2007 / 2008-2014)")
if old in s:
    fm.write_text(s.replace(old, new)); print("forcing_maps.py: EARLY/LATE -> 2001-2014 / 2015-2025")
elif "(2001, 2014), (2015, 2025)" in s:
    print("forcing_maps.py: EARLY/LATE already set")
else:
    sys.exit("forcing_maps.py: EARLY_YEARS line not found")
pat = re.compile(r"^(\s*START_YEAR,\s*END_YEAR\s*=\s*)2001,\s*2014\b", re.M)
for name in sys.argv[1:]:
    p = Path(f"analysis/{name}.ipynb"); nb = json.loads(p.read_text()); n = 0
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]); src2, k = pat.subn(r"\g<1>2001, 2025", src)
        if k:
            c["source"] = src2.splitlines(keepends=True); n += k
    already = any(re.search(r"START_YEAR,\s*END_YEAR\s*=\s*2001,\s*2025", "".join(c["source"])) for c in nb["cells"])
    if n == 0 and not already:
        sys.exit(f"{name}: START_YEAR, END_YEAR = 2001, 2014 not found")
    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: START/END_YEAR -> 2001, 2025 ({n} line(s))")
EOF
log "notebooks + forcing_maps patched"

# 7. run (outputs saved in the notebooks; logs results/tables/logs/run_<nb>_2001-2025.log)
run_nb() {
    nb=$1; L="results/tables/logs/run_${nb}_2001-2025.log"; t0=$(date +%s)
    "$PY" results/tables/logs/run_nb_inplace.py "analysis/$nb.ipynb" --timeout 21600 > "$L" 2>&1; rc=$?
    echo "$(date '+%F %T') $nb EXIT $rc ($(( ($(date +%s) - t0) / 60 )) min) log $L"
}
export -f run_nb; export PY
log "running $NPAR in parallel: $(echo $NBS)"
echo $NBS | tr ' ' '\n' | xargs -P $NPAR -I{} bash -c 'run_nb {}' >> "$ST/run.log" 2>&1

# 8. summary
{
    echo "2001-2025 analysis run (session 4f89c2b2 script), finished $(date '+%F %T')"
    grep -E ' EXIT [0-9]+ ' "$ST/run.log"
    echo "new figures *_2001_2025*: $(find results/figures analysis -name '*2001_2025*.png' -newer "$ST/backup/forcing_maps.py" | wc -l)"
    echo "new tables  *_2001_2025*: $(find results/tables analysis -name '*2001_2025*.csv' -newer "$ST/backup/forcing_maps.py" | wc -l)"
    echo "NOTE: markdown text in the notebooks still quotes 2001-2014 numbers; LCC_FUT_fBVOClccFUT = design-B stand-in."
} > "$ST/SUMMARY.txt"
cat "$ST/SUMMARY.txt" >> "$ST/run.log"
if grep -qE ' EXIT [1-9]' "$ST/run.log"; then echo "some notebooks failed, see SUMMARY.txt" > "$ST/FAILED"; else touch "$ST/DONE"; fi
log "end"
