"""Style test: broadleaf/needleleaf border on the isoprene and monoterpene emission maps.

Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).

The border is made of grid-cell edges. Pieces marked by the user are removed, the two gaps in
Norway and Siberia are reconnected, and cells with the border on three sides get a dashed fourth side:
  A = keep the three sides, add the dashed side
  B = replace the three sides with the dashed side
"""
import sys
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from shapely.ops import linemerge

import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

LINE_WIDTH = 1.5
DASHES = (0, (1.2, 0.9))
ROWS = [("LCC_PD", "CTRL_PD"), ("LCC_FUT", "CTRL_FUT")]
LABELS = ["[LCC − CTRL]_PD", "[LCC − CTRL]_FUT"]
# Boxes marked by the user on the map (2026-11-21), pixels of the screenshot: x0, y0, x1, y1.
MAP_PIXELS = (45, 38, 898, 890)  # left, top, right, bottom of the map circle in that screenshot
REMOVE_BOXES = [(301, 101, 380, 201), (237, 200, 294, 291), (538, 101, 650, 201)]
RECONNECT_BOXES = {"Siberia": (635, 617, 682, 656), "Norway": (483, 714, 530, 758)}


class Grid:
    def __init__(self, classes):
        self.lat, self.lon = classes["lat"].values, classes["lon"].values
        self.nlat, self.nlon = self.lat.size, self.lon.size
        dlon = np.diff(self.lon).mean()
        self.lon_edges = self.lon[0] - dlon / 2 + dlon * np.arange(self.nlon + 1)
        self.lat_edges = np.r_[self.lat[0], 0.5 * (self.lat[:-1] + self.lat[1:]), self.lat[-1]]

    def edge(self, a, b):
        a, b = (a[0], a[1] % self.nlon), (b[0], b[1] % self.nlon)
        return (a, b) if a <= b else (b, a)

    def sides(self, i, j):
        return [self.edge((i, j), (i, j + 1)), self.edge((i + 1, j), (i + 1, j + 1)),
                self.edge((i, j), (i + 1, j)), self.edge((i, j + 1), (i + 1, j + 1))]

    def coords(self, edge):
        (ia, ja), (ib, jb) = edge
        if abs(ja - jb) > 1:  # edge across the longitude seam
            ja, jb = [self.nlon if j == 0 else j for j in (ja, jb)]
        return np.array([[self.lon_edges[ja], self.lat_edges[ia]], [self.lon_edges[jb], self.lat_edges[ib]]])


def border_edges(grid, classes):
    """Grid-cell edges where a broadleaf cell touches a needleleaf cell."""
    group = np.where(classes.isin([1, 2]), 1, np.where(classes == 3, 2, 0))
    edges = set()
    for i in range(grid.nlat):
        for j in range(grid.nlon):
            if {group[i, j], group[i, (j + 1) % grid.nlon]} == {1, 2}:
                edges.add(grid.edge((i, j + 1), (i + 1, j + 1)))
            if i + 1 < grid.nlat and {group[i, j], group[i + 1, j]} == {1, 2}:
                edges.add(grid.edge((i + 1, j), (i + 1, j + 1)))
    return edges


def in_box(grid, edges, ax, pixel_box):
    left, top, right, bottom = MAP_PIXELS
    x0, y0, x1, y1 = pixel_box
    a, c = (x0 - left) / (right - left), (x1 - left) / (right - left)
    b, d = (bottom - y1) / (bottom - top), (bottom - y0) / (bottom - top)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    inside = set()
    for edge in edges:
        mx, my = grid.coords(edge).mean(axis=0)
        px, py = ax.projection.transform_point(mx, my, ccrs.PlateCarree())
        fx, fy = (px - xlim[0]) / (xlim[1] - xlim[0]), (py - ylim[0]) / (ylim[1] - ylim[0])
        if a <= fx <= c and b <= fy <= d:
            inside.add(edge)
    return inside


def neighbours(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)
    return graph


def components(edges):
    graph, label = neighbours(edges), {}
    for start in graph:
        if start in label:
            continue
        label[start] = start
        queue = deque([start])
        while queue:
            for node in graph[queue.popleft()]:
                if node not in label:
                    label[node] = start
                    queue.append(node)
    return label


def shortest_connection(grid, kept, removed):
    """Fewest removed edges joining two separate pieces of the kept line."""
    label, graph = components(kept), neighbours(removed)
    best = None
    for start in (n for n in graph if n in label):
        previous, queue = {start: None}, deque([start])
        while queue:
            node = queue.popleft()
            if node in label and label[node] != label[start]:
                path = []
                while previous[node] is not None:
                    path.append(grid.edge(node, previous[node]))
                    node = previous[node]
                if best is None or len(path) < len(best):
                    best = path
                break
            for other in graph[node]:
                if other not in previous:
                    previous[other] = node
                    queue.append(other)
    return best or []


def edited_border(grid, classes, ax):
    original = border_edges(grid, classes)
    marked = set().union(*(in_box(grid, original, ax, b) for b in REMOVE_BOXES))
    gaps = {name: in_box(grid, original, ax, b) for name, b in RECONNECT_BOXES.items()}
    kept = original - marked - set().union(*gaps.values())
    for name, removed in gaps.items():
        path = shortest_connection(grid, kept, removed)
        kept |= set(path)
        print(f"{name}: restored {len(path)} of {len(removed)} marked edges")
    print(f"border: {len(original)} original edges, {len(kept)} kept")
    return kept


def three_sided(grid, solid, replace_sides):
    """Dashed open side for every cell with the border on exactly three sides."""
    solid, dashed, touched, cells = set(solid), set(), set(), 0
    for i in range(grid.nlat):
        for j in range(grid.nlon):
            sides = grid.sides(i, j)
            present = [s for s in sides if s in solid]
            if len(present) != 3 or any(s in touched for s in sides):
                continue
            cells += 1
            dashed.add(next(s for s in sides if s not in solid))
            if replace_sides:
                solid -= set(present)
                touched |= set(sides)
    print(f"three-sided cells: {cells}; replace sides: {replace_sides}")
    return solid, dashed


def draw(ax, grid, solid, dashed):
    merged = linemerge([LineString(grid.coords(e)) for e in solid])
    for line in getattr(merged, "geoms", [merged]):
        xy = np.asarray(line.coords)
        ax.plot(xy[:, 0], xy[:, 1], color="black", lw=LINE_WIDTH, solid_capstyle="projecting",
                solid_joinstyle="miter", transform=ccrs.PlateCarree(), zorder=6)
    for edge in dashed:
        xy = grid.coords(edge)
        ax.plot(xy[:, 0], xy[:, 1], color="black", lw=LINE_WIDTH, ls=DASHES, dash_capstyle="butt",
                transform=ccrs.PlateCarree(), zorder=6)


def emission_grid(panels):
    for attempt in range(1, 9):  # NIRD reads fail intermittently with "HDF error"
        try:
            return fm.make_contrast_grid_figure("LCC-CTRL", panels, "BVOC emissions", start_year=tv.START,
                                                end_year=tv.END, rows=ROWS, labels=LABELS, save=False)
        except (OSError, RuntimeError) as err:
            print(f"read attempt {attempt} failed: {err}", flush=True)
            plt.close("all")
            if attempt == 8:
                raise
            time.sleep(10 * attempt)


def main():
    set_default_style()
    classes = tv.load_classes()[2]
    grid = Grid(classes)
    panels = [p for p in fm.CONTEXT_PANELS if p.key in ("sfisop", "sfmterp")]
    kept = None
    for name, replace_sides in (("A", False), ("B", True)):
        fig, axes = emission_grid(panels)
        if kept is None:
            kept = edited_border(grid, classes, axes[0, 0])
        solid, dashed = three_sided(grid, kept, replace_sides)
        for ax in axes.flat:
            draw(ax, grid, solid, dashed)
        fig.savefig(tv.OUT / f"bvoc_emissions_border_{name}.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
