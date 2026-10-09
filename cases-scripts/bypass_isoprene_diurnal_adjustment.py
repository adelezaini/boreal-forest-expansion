#!/usr/bin/env python3
"""Disable the extra prescribed-isoprene diurnal adjustment in a case-local reader.

Usage:
    python3 bypass_isoprene_diurnal_adjustment.py SourceMods/src.cam/mo_srf_emissions.F90

Copy the reader into the fBVOC case's SourceMods before calling this script.
Use only when prescribed total ISOP already contains its diurnal cycle.
Creates a .before_fbvoc backup and leaves an already patched file unchanged.
Does not change MTERP or disable interactive emissions. Rebuild CAM afterwards.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


def patch_reader(path):
    text = path.read_text()
    marker = "! fBVOC: prescribed total ISOP already contains its diurnal cycle."

    # Restrict the edit to the block following this specific comment.
    heading = re.compile(r"^[ \t]*!.*adjust isoprene for diurnal variation.*$", re.M | re.I)
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        raise ValueError("expected exactly one isoprene diurnal-adjustment heading.")
    start = matches[0].end()

    # Skip blank/comment lines to find the first executable statement.
    statement = re.search(r"^[ \t]*(?![ \t!])\S[^\n]*", text[start:], re.M)
    if statement is None:
        raise ValueError("no statement found after the isoprene heading.")
    line = statement.group()
    before = text[start:start + statement.start()]

    if re.fullmatch(r"\s*if\s*\(\s*\.false\.\s*\)\s*then\s*", line, re.I):
        if marker in before:
            print(f"Already patched: {path}")
            return
        raise ValueError("block is already disabled without the expected marker; inspect it.")
    if not re.fullmatch(r"\s*if\s*\(\s*isop_ndx\s*>\s*0\s*\)\s*then\s*", line, re.I):
        raise ValueError(f"unexpected statement; no changes made:\n{line}")

    backup = path.with_name(path.name + ".before_fbvoc")
    if backup.exists():
        raise ValueError(f"backup already exists; inspect it before patching: {backup}")
    shutil.copy2(path, backup)

    indent = re.match(r"[ \t]*", line).group()
    replacement = f"{indent}{marker}\n{indent}if( .false. ) then"
    a, b = start + statement.start(), start + statement.end()
    path.write_text(text[:a] + replacement + text[b:])
    print(f"Patched: {path}")
    print(f"Backup:  {backup}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("reader", type=Path, help="Case-local SourceMods reader to patch")
    args = parser.parse_args()
    try:
        patch_reader(args.reader)
    except (OSError, ValueError) as exc:
        sys.exit(f"ERROR: {exc}")
