"""Layout test (2026-11-25): forest/climate ratio chart of analysis/climate-vs-lcc-land-temperature.ipynb (cell 6),
horizontal bars with short labels; reads the 2001-2040 table, writes only to sandbox/test_land_temp_ratio_outputs/."""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
REPO = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
C = pd.read_csv(REPO / "results/tables/climate-vs-lcc-land-temperature/climate_vs_forest_comparison_2001_2040.csv")
NAVY, RED = "#2E3A8C", "#BC4540"
SHORT = {"TOA net radiation": "TOA net radiation", "surface-albedo proxy": "surface-albedo SW proxy",
         "2 m air temperature": "2 m air temperature", "skin temperature": "skin temperature"}
sub = C[(C["region"] == "modified cells") & (C["season"] != "SON")].copy()
sub["name"] = sub["measure"].str.replace(r" \(.*$", "", regex=True).str.replace(r",.*$", "", regex=True)
sub["label"] = sub["name"].map(lambda s: SHORT.get(s, s)) + ", " + sub["season"]
sub = sub.iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.6))
y = np.arange(len(sub))
col = [RED if "temperature" in n else NAVY for n in sub["name"]]
ax.barh(y, sub["forest_over_climate_pct"], color=col, height=0.7)
for yi, v in zip(y, sub["forest_over_climate_pct"]):
    ax.text(v + 0.3, yi, f"{v:.1f} %", va="center", fontsize=9)
ax.set_yticks(y, sub["label"], fontsize=9)
ax.set_xlabel("forest signal / climate signal [%]\nforest = [LCC − CTRL]_FUT, climate = CTRL_[FUT − PD]")
ax.set_title("Forest-expansion signal relative to the climate-change signal\nmodified cells, 2001–2040 "
             "· navy: radiation (annual) · red: land temperature", fontsize=11)
ax.set_xlim(0, max(sub["forest_over_climate_pct"]) * 1.15)
for s in ("top", "right"): ax.spines[s].set_visible(False)
out = REPO / "sandbox/test_land_temp_ratio_outputs/forest_over_climate_ratio_2001_2040.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white"); print("Saved", out)
