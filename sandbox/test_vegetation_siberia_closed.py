"""Style test: close the central Siberia gap of the dashed border along the route sketched by the user.

Prints the classes on both sides of each new cell edge. Saves a candidate line file; the approved
vegetation_map_lines.json is not changed. Rows = variables (LCC_FUT - CTRL_FUT), columns = current / closed.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import matplotlib.pyplot as plt
import numpy as np

import test_vegetation_border_styles as ts
import test_vegetation_line_colours as tc
import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from test_vegetation_russia_gap import joining_path
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

CANDIDATE = tv.OUT / "vegetation_map_lines_siberia_closed.json"
SOURCE = tv.OUT / "vegetation_map_lines_before_siberia.json"  # line file approved before these hand edits
RESTORE_MODIFIED = {"Sweden": ((12.5, 58.74), (17.5, 60.63)), "Estonia": ((26.25, 59.68), (30.0, 58.74))}
ALASKA_PIECES = 9, 6  # joined by the 124 km class border between 201.25E 61.58N and 200E 62.53N
SMOOTH_PASSES = 2
SOUTH_PIECE, NORTH_PIECE = 1, 5  # piece 1 ends at 103.8E 54.9N, piece 5 starts at 98.8E 58.7N
NAMES = {0: "small gain", 1: "broadleaf", 3: "other tree gain"}
VARIABLES = [(fm.CONTEXT_PANELS, "sfmterp"), (fm.forcing_panels("NET"), "total")]
PAIRS = {"case1": "LCC_FUT", "case2": "CTRL_FUT"}


def name(version, lon, lat):
    value = version.sel(lon=lon, lat=lat, method="nearest").item()
    return "unmodified" if np.isnan(value) else NAMES[int(value)]


def sketch_route(version, south_end, north_end):
    """Route drawn by the user: north along 103.75E, then west along the north edge of the orange patch."""
    lats = version["lat"].values
    i = int(np.argmin(np.abs(lats - 57.79)))
    low, top = (lats[i - 1] + lats[i]) / 2, (lats[i] + lats[i + 1]) / 2  # vertices of the existing 211 km class border
    return np.array([[103.75, lats[i - 1]], [103.75, low], [103.75, lats[i]], [103.75, top], [102.5, top], [100.0, top]])


def smooth(xy, passes=SMOOTH_PASSES):
    """Round the corners (Chaikin), keeping both end points."""
    for _ in range(passes):
        a, b = xy[:-1], xy[1:]
        xy = np.vstack([xy[0], np.column_stack([0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]).reshape(-1, 2), xy[-1]])
    return xy


def check_edges(version, south_end, north_end):
    dlon, dlat = np.diff(version["lon"].values).mean(), np.diff(version["lat"].values).mean()
    for cell_lat in version["lat"].sel(lat=[55.89, 57.79], method="nearest").values:
        print(f"edge at 103.75E, {cell_lat:.1f}N: west {name(version, 103.75 - dlon / 2, cell_lat)}, "
              f"east {name(version, 103.75 + dlon / 2, cell_lat)}")
    for cell_lon in (100.0, 102.5):
        print(f"edge at {north_end[1]:.2f}N, {cell_lon:.1f}E: north {name(version, cell_lon, north_end[1] + dlat / 2)}, "
              f"south {name(version, cell_lon, north_end[1] - dlat / 2)}")


def restore_modified(pieces, mask):
    """Put back the stretches of the land-only modified line named in RESTORE_MODIFIED."""
    with tr.xr.open_dataset(tv.LCC_SURF, decode_times=False) as surf:
        landfrac = surf["LANDFRAC_PFT"].load().values
    full, lon_c = tr.tm.modified_contour(mask)
    land = tr.tm.land_edges(full, mask, landfrac > tr.tf.LAND_LIMIT, lon_c)
    pieces = list(pieces)
    for name, (a, b) in RESTORE_MODIFIED.items():
        path = joining_path(land, a, b)
        if path is None:
            raise ValueError(f"{name}: no land-only line joins {a} and {b}")
        path = np.round(path, 6)
        print(f"restored {name}: {ts.length_km(path):.0f} km")
        for k, xy in enumerate(pieces):
            if np.allclose(path[0], xy[0]):
                pieces[k] = np.vstack([path[::-1], xy[1:]])
                break
            if np.allclose(path[-1], xy[0]):
                pieces[k] = np.vstack([path, xy[1:]])
                break
        else:
            pieces.append(path)
    return pieces


def main():
    set_default_style()
    _, _, classes, mask, _ = tv.load_classes()
    version = classes.where(classes != 2, 3)
    stored = json.loads(SOURCE.read_text())
    current = {k: [np.asarray(xy) for xy in stored[k]] for k in ("border", "modified")}
    south, north = current["border"][SOUTH_PIECE], current["border"][NORTH_PIECE]
    route = sketch_route(version, south[-1], north[0])
    check_edges(version, south[-1], north[0])
    stretch = smooth(np.vstack([south[-2:], route, north[:2]]))
    joined = np.vstack([south[:-2], stretch, north[2:]])
    print(f"smoothed stretch: {ts.length_km(stretch):.0f} km")
    alaska = np.vstack([current["border"][ALASKA_PIECES[0]], current["border"][ALASKA_PIECES[1]]])
    print(f"west Alaska joined: {ts.length_km(alaska):.0f} km; open ends "
          f"{np.round(alaska[0], 2).tolist()} and {np.round(alaska[-1], 2).tolist()}, "
          f"{ts.length_km(np.array([alaska[0], alaska[-1]])):.0f} km apart")
    dropped = (SOUTH_PIECE, NORTH_PIECE, *ALASKA_PIECES)
    border = [xy for k, xy in enumerate(current["border"]) if k not in dropped] + [joined, alaska]
    closed = {"border": border, "modified": restore_modified(current["modified"], mask)}
    CANDIDATE.write_text(json.dumps({
        "description": stored["description"] + " Candidate: central Siberia gap closed along the route sketched by the user, smoothed; west Alaska segment restored, modified line restored in Estonia and Sweden.",
        "border": [np.round(xy, 6).tolist() for xy in border],
        "modified": [np.round(xy, 6).tolist() for xy in closed["modified"]]}))

    panels = [replace(next(p for p in group if p.key == key), case1_role="case1", case2_role="case2")
              for group, key in VARIABLES]
    data = [tc.read(panel, PAIRS) for panel in panels]
    versions = [("Current: gap in central Siberia", current), ("Candidate: smoothed route, Alaska joined", closed)]
    fig, axes = fm.map_grid(len(panels), len(versions), titles_every_row=True)
    for i, (panel, d) in enumerate(zip(panels, data)):
        vmax = fm.symmetric_vmax(d.mean("year").where(d["lat"] >= 45.0))
        for j, (title, lines) in enumerate(versions):
            ax = axes[i, j]
            fm._plot_panel(ax, panel, PAIRS, tv.START, tv.END, 45.0, 45.0, True, tc.FDR_ALPHA, vmax=vmax, d=d)
            ax.set_title(f"{title}\n{panel.title}" if i == 0 else panel.title, fontsize=8.5, fontweight="semibold")
            tr.add_lines(ax, lines)
    fig.suptitle(f"Dashed border over Russia: LCC_FUT − CTRL_FUT, {tv.START}–{tv.END}", fontsize=12, y=1.0)
    fig.savefig(tv.OUT / "siberia_gap_closed.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
