#!/usr/bin/env python3
"""Tables of the fields in the CAM and CLM h0 files, with metadata.

Writes to docs/history-output/:
  cam_h0_fields.csv, clm_h0_fields.csv  every variable in one h0 file of each component
  added_fields_<tag>.csv                whitelist fields added since git revision --base

Usage ($PY = lcc-env python):
  $PY make_history_field_tables.py CAM_H0 CLM_H0 [--base HEAD] [--tag 20261028]
      [--fbvoc-atm-log atm.log.gz]

- Whitelists are parsed from cases-scripts/cases-setup.sh (working tree vs --base).
- absent_in_fBVOC: CAM = name not in the master list of an fBVOC run (atm.log, MEGAN off);
  CLM = name only requested by `clm_diagnostics std` (MEG_*, EPS_*, GAMMA*).
- est_MB_per_month = 4 bytes x non-time dims, uncompressed (the files are netCDF-4 compressed).
"""
import argparse
import csv
import gzip
import re
import subprocess
import sys
from pathlib import Path

import xarray as xr

REPO = Path(__file__).resolve().parents[2]
SETUP = "cases-scripts/cases-setup.sh"
OUT = REPO / "docs" / "history-output"
sys.path.insert(0, str(REPO / "src"))
from boreal_forest_expansion.postprocess.variables import CATEGORIES  # noqa: E402

FBVOC_ATM_LOG = ("/cluster/work/users/adelez/archive/"
                 "NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261025/logs/")

# Purpose groups of the fields added on 2026-10-28 (first matching pattern wins)
GROUPS = [
    (r"^(QFLX|PBLH|RELHUM|TMQ)$", "humidity / boundary layer"),
    (r"^cb_", "column burden"),
    (r"^(NO3|N2O5|HNO3|PAN|H2O2)$", "oxidants / nitrogen reservoirs"),
    (r"^(CH2O|MACR|MVK|ISOPOOH|IEPOX|ISOPNO3|TERPNIT|TERPROD\d)$", "BVOC oxidation products"),
    (r"^(DMS|SO2)$", "sulfur"),
    (r"^SF", "surface emission flux"),
    (r"^(DF|WD)_", "gas dry/wet deposition"),
    (r"^SOA_.*OCW", "cloud-borne SOA removal"),
    (r"^SOA_.*(GVF|TBF)$", "SOA dry deposition (grav./turb.)"),
    (r"^(NCONC|NMR)\d\d$", "aerosol number / size per mode"),
    (r"^(Z0|DISPLA)", "roughness / displacement"),
    (r"^(RAM1|RSSUN|RSSHA|RH2M)$", "resistance / stomata / humidity"),
    (r"^(FCTR|FCEV|FGEV)$", "latent heat split"),
    (r"^(ALB|SAB|FSR)", "albedo / absorbed solar"),
    (r"^SNOFS", "snow radiation"),
    (r"^(H2OCAN|HBOT|TOT)", "canopy / carbon storage"),
]


def heredoc_names(text, start):
    """Quoted names from the heredoc line starting with `start` up to its EOF."""
    i = text.index(start)
    return re.findall(r"'([^']+)'", text[i:text.index("\nEOF", i)])


def whitelists(text):
    clm_std = heredoc_names(text, "hist_fincl1 += 'MEG_isoprene'")
    return {"atm": heredoc_names(text, "fincl1 = 'FSNT'"),
            "lnd": heredoc_names(text, "hist_fincl1 = 'FSA'") + clm_std}, set(clm_std)


def master_names(log):
    opener = gzip.open if str(log).endswith(".gz") else open
    names, on = set(), False
    with opener(log, "rt") as f:
        for line in f:
            if "MASTER FIELD LIST" in line:
                on = True
            elif on and re.match(r"^\s*\d+\s+\S", line):
                names.add(line.split()[1])
            elif on and names:
                break
    return names


def rows(path, comp, wanted, added, fbvoc_absent):
    category = {v: c for c, vs in CATEGORIES[comp].items() for v in vs}
    ds = xr.open_dataset(path, decode_times=False)
    for name, da in ds.variables.items():
        dims = [d for d in da.dims if d != "time"]
        spatial = {"lat", "lon", "lndgrid"} & set(da.dims)
        kind = ("whitelist" if name in wanted else
                "default" if "time" in da.dims and spatial else "grid/coord")
        nlev = next((ds.sizes[d] for d in dims if d not in ("lat", "lon", "lndgrid")), "")
        size = 4
        for d in dims:
            size *= ds.sizes[d]
        yield {"component": "CAM" if comp == "atm" else "CLM", "name": name,
               "long_name": da.attrs.get("long_name", ""), "units": da.attrs.get("units", ""),
               "dims": ",".join(da.dims), "n_lev": nlev,
               "cell_methods": da.attrs.get("cell_methods", ""), "kind": kind,
               "added": name in added,
               "group": next((g for p, g in GROUPS if re.search(p, name)), "") if name in added else "",
               "absent_in_fBVOC": name in fbvoc_absent,
               "postprocess_category": category.get(name, ""),
               "est_MB_per_month": round(size / 1e6, 3) if spatial else ""}
    ds.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("cam_h0")
    ap.add_argument("clm_h0")
    ap.add_argument("--base", default="HEAD", help="git revision with the old whitelists")
    ap.add_argument("--tag", default="20261028")
    ap.add_argument("--fbvoc-atm-log", default=None)
    a = ap.parse_args()

    new, clm_std = whitelists((REPO / SETUP).read_text())
    old, _ = whitelists(subprocess.run(["git", "-C", str(REPO), "show", f"{a.base}:{SETUP}"],
                                       check=True, capture_output=True, text=True).stdout)
    log = a.fbvoc_atm_log or sorted(Path(FBVOC_ATM_LOG).glob("atm.log.*"))[0]
    fbvoc_cam = master_names(log)
    absent = {"atm": {v for v in new["atm"] if v not in fbvoc_cam}, "lnd": clm_std}

    OUT.mkdir(parents=True, exist_ok=True)
    added_rows = []
    for comp, path, fname in [("atm", a.cam_h0, "cam_h0_fields.csv"),
                              ("lnd", a.clm_h0, "clm_h0_fields.csv")]:
        added = set(new[comp]) - set(old[comp])
        table = list(rows(path, comp, set(new[comp]), added, absent[comp]))
        with open(OUT / fname, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=table[0].keys())
            w.writeheader()
            w.writerows(table)
        in_file = {r["name"] for r in table}
        added_rows += [r for r in table if r["added"]]
        print(f"{fname}: {len(table)} variables, whitelist {len(set(new[comp]))}, "
              f"added {len(added)}, kinds "
              f"{ {k: sum(r['kind'] == k for r in table) for k in ('whitelist', 'default', 'grid/coord')} }")
        missing = sorted(set(new[comp]) - in_file)
        if missing:
            print(f"  whitelist names NOT in {Path(path).name}: {missing}")
    keep = ["component", "name", "long_name", "units", "dims", "n_lev", "cell_methods", "group",
            "est_MB_per_month", "absent_in_fBVOC", "postprocess_category"]
    with open(OUT / f"added_fields_{a.tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keep, extrasaction="ignore")
        w.writeheader()
        w.writerows(added_rows)
    print(f"added_fields_{a.tag}.csv: {len(added_rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
