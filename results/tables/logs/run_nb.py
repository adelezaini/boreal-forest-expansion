"""Run a notebook's code cells headless (no jupyter needed); print extra expressions at the end."""
import json, os, sys, time, matplotlib
matplotlib.use("Agg")
import pandas as pd
pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 400)
NB = os.path.abspath(sys.argv[1]); os.chdir(os.path.dirname(NB))
ns = {"display": lambda x: print(x.data if hasattr(x, "data") else x)}
for i, c in enumerate(json.load(open(NB))["cells"]):
    if c["cell_type"] != "code": continue
    t = time.time(); exec("".join(c["source"]), ns); print(f"--- cell {i} ok ({time.time()-t:.0f}s)", flush=True)
for expr in sys.argv[2:]:
    v = eval(expr, ns)
    print(f"\n##### {expr}\n", v.to_string() if hasattr(v, "to_string") else v, flush=True)
