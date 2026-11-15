"""Shrink the figures embedded in a notebook so the .ipynb stays under GitHub's 100 MB file limit.

Usage: python shrink_nb_images.py nb1.ipynb [nb2.ipynb ...] [--min-mb 20]

Every image/png output is re-encoded as a 256-colour PNG at full resolution (same size in pixels).
Checked on radiative_forcing.ipynb (130 figures, 15 Nov 2026): 112 -> ~42 MB; mean pixel change
0.7-1.2 on the 0-255 scale, no visible difference. The PNG files in results/figures are not touched.
- An image is only replaced if the new one is smaller; images that are already 256-colour are skipped,
  so running it twice changes nothing.
- Images with real transparency are left as they are.
- Notebooks smaller than --min-mb are skipped (default 20 MB).
run_nb_inplace.py calls shrink() at the end of each run.
"""
import argparse, base64, io, json, os

from PIL import Image

DEFAULT_MIN_MB = 20


def _shrink_png(b64):
    raw = base64.b64decode(b64)
    im = Image.open(io.BytesIO(raw))
    if im.mode == 'P':
        return None  # already 256-colour
    if im.mode in ('RGBA', 'LA'):
        if im.getchannel('A').getextrema()[0] < 255:
            return None  # real transparency: keep as is
    im = im.convert('RGB')
    out = io.BytesIO()
    im.quantize(256).save(out, 'PNG', optimize=True)
    if out.tell() >= len(raw):
        return None
    return base64.b64encode(out.getvalue()).decode('ascii') + '\n'


def shrink(path, min_mb=DEFAULT_MIN_MB, verbose=True):
    """Re-encode the embedded PNGs of `path` in place. Returns (MB before, MB after)."""
    before = os.path.getsize(path) / 1e6
    if before < min_mb:
        if verbose:
            print(f'{path}: {before:.1f} MB < {min_mb} MB, skipped')
        return before, before
    nb = json.load(open(path))
    changed = 0
    for cell in nb.get('cells', []):
        for out in cell.get('outputs', []):
            data = out.get('data', {})
            png = data.get('image/png')
            if not png:
                continue
            new = _shrink_png(png if isinstance(png, str) else ''.join(png))
            if new is not None:
                data['image/png'] = new
                changed += 1
    if changed:
        tmp = path + '.shrink-tmp'
        json.dump(nb, open(tmp, 'w'), indent=1, ensure_ascii=False)
        os.replace(tmp, path)
    after = os.path.getsize(path) / 1e6
    if verbose:
        print(f'{path}: {before:.1f} -> {after:.1f} MB ({changed} figures re-encoded)')
    return before, after


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('notebooks', nargs='+')
    p.add_argument('--min-mb', type=float, default=DEFAULT_MIN_MB)
    a = p.parse_args()
    for nb_path in a.notebooks:
        shrink(nb_path, a.min_mb)
