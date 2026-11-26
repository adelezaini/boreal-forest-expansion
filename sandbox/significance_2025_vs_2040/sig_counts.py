"""FDR-significant cell counts >=45N, 2001-2025 vs 2001-2040 (same test as the maps: t-test + BH FDR 0.10)."""
import sys, time
sys.path.insert(0, "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/src")
import pandas as pd
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.analysis.stats import cellwise_pvalue, fdr_mask
PAIRS = {
 "total PD [LCC-CTRL]_PD": ("LCC_PD", "CTRL_PD"), "total FUT [LCC-CTRL]_FUT": ("LCC_FUT", "CTRL_FUT"),
 "non-BVOC PD": ("LCC_PD_fBVOCctrlPD", "CTRL_PD_fBVOCctrlPD"), "non-BVOC FUT": ("LCC_FUT_fBVOCctrlFUT", "CTRL_FUT_fBVOCctrlFUT"),
 "BVOC (1) PD": ("LCC_PD_fBVOClccPD", "LCC_PD_fBVOCctrlPD"), "BVOC (2) FUT": ("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOCctrlFUT"),
 "BVOC (3) climate": ("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOClccPD"), "climate CTRL_[FUT-PD]": ("CTRL_FUT", "CTRL_PD"),
}
VARS = [("RADIATIVE", "NET_toa"), ("RADIATIVE", "NET_cloud"), ("SOA", "cbSOA_mgm2")]
rows = []
for name, (a, b) in PAIRS.items():
    for cls, var in VARS:
        for y1 in (2025, 2040):
            for k in range(5):
                try:
                    d = fm.yearly_difference(a, b, cls, var, 2001, y1).load(); break
                except Exception as e:
                    print("retry", name, var, y1, e, flush=True); time.sleep(30)
            north = d["lat"] >= 45
            sig = fdr_mask(cellwise_pvalue(d), 0.10, within=north)
            n = int((north.broadcast_like(sig) & sig.notnull()).sum()); ns = int((sig & north).sum())
            rows.append(dict(contrast=name, var=var, years=f"2001-{y1}", sig=ns, cells=n, pct=100 * ns / n))
            print(rows[-1], flush=True)
t = pd.DataFrame(rows)
t.to_csv(sys.argv[1], index=False)
print(t.pivot_table(index=["contrast", "var"], columns="years", values="pct", sort=False).round(1).to_string())
