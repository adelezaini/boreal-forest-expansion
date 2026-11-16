#!/bin/bash
# 2001-2040 analysis (user 2026-11-11; plan approved 2026-11-15; record docs/met-nudg-2026-2040.md).
# Started by met_nudg_2026-2040_when_done.sh when all 12 nudged runs are postprocessed for 2001-2040
# (staging, 228 files). Adapted from analysis_2001-2025_when_done.sh.
#
# Steps: 1 wait for 228 files in staging (each run: run_all_parallel + one retry, done by the watcher)
#        -> 2 check the 2001-2025 slice of the new files against the existing 2001-2025 files (rel <= 1e-3)
#        -> 3 move new files into data/processed-data/postprocessing/ (2001-2014 and 2001-2025 files kept)
#        -> 4 keep the 2001-2025 results: cp -an results/figures -> results/figures-2001-2025, results/tables ->
#             results/tables-2001-2025, file counts checked (memory rule, as for figures-2001-2014)
#        -> 5 wait until no other analysis notebook run is active -> 6 patch START/END_YEAR 2001, 2025 -> 2001, 2040
#        in the notebooks + EARLY/LATE_YEARS (2001,2014),(2015,2025) -> (2001,2014),(2015,2040) in forcing_maps.py
#        (backups in $ST/backup) -> 7 run the notebooks (4 in parallel, outputs saved) -> 8 SUMMARY.txt
# State/logs: /cluster/work/users/adelez/analysis-2001-2040/  (run.log, SUMMARY.txt, DONE or FAILED)
# Stop: touch /cluster/work/users/adelez/analysis-2001-2040/STOP
set -u
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
STG=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing-2001-2040-staging
DST=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
ST=/cluster/work/users/adelez/analysis-2001-2040
NBS="radiative_forcing bvoc-soa-cloud-interactions biogeophysical-hydro simulation-contrasts timeseries-responses
pd-fut-attribution fut-fbvoc-emission-source-choice artefact-corrected-split cumulative_radiative_decomposition
land-carbon-water"
NPAR=4
mkdir -p "$ST/backup"
log()  { echo "$(date '+%F %T') $*" >> "$ST/run.log"; }
fail() { log "ERROR: $*"; echo "$(date '+%F %T') $*" > "$ST/FAILED"; exit 1; }
stop() { [[ -f "$ST/STOP" ]] && { log "STOP file found, exiting"; exit 0; }; }
log "start on $(hostname), pid $$"

# 1. all 12 runs postprocessed (the watcher starts this script then; wait anyway, max 24 h)
t0=$(date +%s)
until (( $(ls "$STG"/*_2001-2040.nc 2>/dev/null | wc -l) == 228 )); do
    stop; (( $(date +%s) - t0 > 86400 )) && fail "$(ls "$STG"/*_2001-2040.nc 2>/dev/null | wc -l) of 228 files after 24 h"; sleep 300
done
log "228 files OK"

# 2. 2001-2025 slice of the new files = existing 2001-2025 files (fail > 1e-3 relative, warn > 1e-6)
"$PY" - "$STG" "$DST" >> "$ST/run.log" 2>&1 <<'EOF' || fail "2001-2025 consistency check failed (see run.log)"
import sys, numpy as np, xarray as xr
stg, dst = sys.argv[1:]
checks = [("CTRL_PD", "atm", "RADIATIVE"), ("LCC_FUT_fBVOCctrlFUT", "atm", "SOA"), ("LCC_PD", "lnd", "BVOC"),
          ("CTRL_FUT_fBVOCctrlFUT", "lnd", "HYDRO"), ("LCC_PD_fBVOClccPD", "atm", "CLOUDPROP"), ("LCC_FUT_fBVOClccFUT", "atm", "RADIATIVE")]
bad = 0
for a, comp, cat in checks:
    new = xr.open_dataset(f"{stg}/{a}_{comp}_{cat}_2001-2040.nc")
    old = xr.open_dataset(f"{dst}/{a}_{comp}_{cat}_2001-2025.nc")
    assert new.sizes["time"] == 480, (a, cat, new.sizes["time"])
    sl = new.sel(time=new["time"].dt.year <= 2025)
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

# 3. move into the analysis folder (2001-2014 and 2001-2025 files stay)
for f in "$STG"/*_2001-2040.nc; do [[ -e "$DST/$(basename "$f")" ]] && fail "exists already: $DST/$(basename "$f")"; done
mv "$STG"/*_2001-2040.nc "$DST"/ || fail "mv to $DST failed"
mkdir -p "$DST/logs_2001-2040" && cp -p "$STG"/logs/*.log "$DST/logs_2001-2040/"
log "moved 228 files to $DST (logs in logs_2001-2040/)"

# 4. keep the 2001-2025 results (never overwritten: cp -an; counts checked)
cd "$REPO" || fail "cd $REPO"
for d in figures tables; do
    [[ -e "results/$d-2001-2025" ]] && fail "results/$d-2001-2025 exists already"
    cp -a "results/$d" "results/$d-2001-2025" || fail "copy results/$d"
    n1=$(find "results/$d" -type f | wc -l); n2=$(find "results/$d-2001-2025" -type f | wc -l)
    (( n1 == n2 )) || fail "results/$d-2001-2025 has $n2 files, results/$d $n1"
    log "results/$d -> results/$d-2001-2025 ($n2 files)"
done

# 5. wait for other analysis notebook runs
while pgrep -f "run_nb_inplace.py analysis/" > /dev/null; do stop; log "waiting: other analysis notebook run active ($(pgrep -fa 'run_nb_inplace.py analysis/' | grep -o 'analysis/[^ ]*' | sort -u | tr '\n' ' '))"; sleep 600; done
log "no other analysis notebook run active"

# 6. patch years (at run time, so the other session's latest notebook versions are used)
for nb in $NBS; do cp -p "analysis/$nb.ipynb" "$ST/backup/"; done
cp -p src/boreal_forest_expansion/plotting/forcing_maps.py "$ST/backup/"
"$PY" - $NBS >> "$ST/run.log" 2>&1 <<'EOF' || fail "patching failed (see run.log; backups in $ST/backup)"
import json, re, sys
from pathlib import Path
fm = Path("src/boreal_forest_expansion/plotting/forcing_maps.py")
s = fm.read_text()
old = "EARLY_YEARS, LATE_YEARS = (2001, 2014), (2015, 2025)"
new = "EARLY_YEARS, LATE_YEARS = (2001, 2014), (2015, 2040)"   # 2026-11-15: late = 2015-2040 (MET + nudged runs to 2040)
if old in s:
    fm.write_text(s.replace(old, new)); print("forcing_maps.py: EARLY/LATE -> 2001-2014 / 2015-2040")
elif "(2001, 2014), (2015, 2040)" in s:
    print("forcing_maps.py: EARLY/LATE already set")
else:
    sys.exit("forcing_maps.py: EARLY_YEARS line not found")
pat = re.compile(r"^(\s*START_YEAR,\s*END_YEAR\s*=\s*)2001,\s*2025\b", re.M)
for name in sys.argv[1:]:
    p = Path(f"analysis/{name}.ipynb"); nb = json.loads(p.read_text()); n = 0
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]); src2, k = pat.subn(r"\g<1>2001, 2040", src)
        if k:
            c["source"] = src2.splitlines(keepends=True); n += k
    already = any(re.search(r"START_YEAR,\s*END_YEAR\s*=\s*2001,\s*2040", "".join(c["source"])) for c in nb["cells"])
    if n == 0 and not already:
        sys.exit(f"{name}: START_YEAR, END_YEAR = 2001, 2025 not found")
    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: START/END_YEAR -> 2001, 2040 ({n} line(s))")
EOF
log "notebooks + forcing_maps patched"

# 7. run (outputs saved in the notebooks; logs results/tables/logs/run_<nb>_2001-2040.log)
run_nb() {
    nb=$1; L="results/tables/logs/run_${nb}_2001-2040.log"; t0=$(date +%s)
    "$PY" results/tables/logs/run_nb_inplace.py "analysis/$nb.ipynb" --timeout 21600 > "$L" 2>&1; rc=$?
    echo "$(date '+%F %T') $nb EXIT $rc ($(( ($(date +%s) - t0) / 60 )) min) log $L"
}
export -f run_nb; export PY
log "running $NPAR in parallel: $(echo $NBS)"
echo $NBS | tr ' ' '\n' | xargs -P $NPAR -I{} bash -c 'run_nb {}' >> "$ST/run.log" 2>&1

# 8. summary
{
    echo "2001-2040 analysis run, finished $(date '+%F %T')"
    grep -E ' EXIT [0-9]+ ' "$ST/run.log"
    echo "new figures *_2001_2040*: $(find results/figures analysis -name '*2001_2040*.png' -newer "$ST/backup/forcing_maps.py" | wc -l)"
    echo "new tables  *_2001_2040*: $(find results/tables analysis -name '*2001_2040*.csv' -newer "$ST/backup/forcing_maps.py" | wc -l)"
    echo "NOTE: markdown text in the notebooks still quotes 2001-2025 numbers (check before quoting)."
} > "$ST/SUMMARY.txt"
cat "$ST/SUMMARY.txt" >> "$ST/run.log"
if grep -qE ' EXIT [1-9]' "$ST/run.log"; then echo "some notebooks failed, see SUMMARY.txt" > "$ST/FAILED"; else touch "$ST/DONE"; fi
log "end"
