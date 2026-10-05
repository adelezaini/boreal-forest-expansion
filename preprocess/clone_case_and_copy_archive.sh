#!/usr/bin/env bash
# Problem: the FUT land-only experiment was named incorrectly: 
# I2100ssp585Clm50BgcCropCplHist_f19_f19-test-20260924 -> I2100ssp585Clm50BgcCropCplHist_f19_f19-20260924
# This script creates a correctly named CIME case and a separately named copy of its archive.
#
# This script does not build or submit a case. The new case is configuration
# only. Its cloned settings should be checked before using it for a future run.
# Renamed restart filenames and rpointer files are NOT proof that a new case
# can restart from them; verify RUN_REFCASE, date and restart set separately.
# NetCDF attributes, logs and other file contents keep the historical name.

set -euo pipefail

old=I2100ssp585Clm50BgcCropCplHist_f19_f19-test-20260924
new=I2100ssp585Clm50BgcCropCplHist_f19_f19-20260924
cases="$HOME/cases/BRL_FRST_XPSN"
archives="/cluster/work/users/$USER/archive"
old_case="$cases/$old"
new_case="$cases/$new"
old_archive="$archives/$old"
new_archive="$archives/$new"

[[ -d "$old_case" ]] || { echo "Missing case: $old_case" >&2; exit 1; }
[[ -d "$old_archive" ]] || { echo "Missing archive: $old_archive" >&2; exit 1; }

# An archive at the destination could belong to another run, or be a previous
# copy. Never overwrite it or merge its files with this archive.
[[ ! -e "$new_archive" && ! -L "$new_archive" ]] || {
    echo "Destination archive already exists: $new_archive" >&2
    echo "Inspect it before running this script again." >&2
    exit 1
}

# The new noresm directory has already been observed on Betzy. If no new case
# accompanies it, stop: cloning could otherwise point at someone else's build.
if [[ ! -d "$new_case" && -d "/cluster/work/users/$USER/noresm/$new" ]]; then
    if [[ -n $(find "/cluster/work/users/$USER/noresm/$new" -mindepth 1 -print -quit) ]]; then
        echo "A nonempty noresm/$new exists without a matching case." >&2
        echo "Inspect that directory before cloning." >&2
        exit 1
    fi
fi

if [[ -d "$new_case" ]]; then
    # A previous invocation may already have created the clone. Check its
    # identity rather than modifying it or making a second case.
    actual_case=$(cd "$new_case" && ./xmlquery --value CASE)
    actual_root=$(cd "$new_case" && ./xmlquery --value CASEROOT)
    [[ "$actual_case" == "$new" && "$actual_root" == "$new_case" ]] || {
        echo "Existing destination case does not match: $new_case" >&2
        exit 1
    }
    echo "Verified existing case: $new_case"
else
    cimeroot=$(cd "$old_case" && ./xmlquery --value CIMEROOT)
    clone_tool="$cimeroot/scripts/create_clone"
    [[ -x "$clone_tool" ]] || { echo "Missing CIME create_clone: $clone_tool" >&2; exit 1; }
    echo "Cloning CIME configuration (no build or submission)..."
    "$clone_tool" --clone "$old_case" --case "$new_case"
fi

# Check that cloning did not leave any output paths pointing at the old case.
# The intended new paths follow the four paths reported by xmlquery above.
expected_exeroot="/cluster/work/users/$USER/noresm/$new/bld"
expected_rundir="/cluster/work/users/$USER/noresm/$new/run"
actual_exeroot=$(cd "$new_case" && ./xmlquery --value EXEROOT)
actual_rundir=$(cd "$new_case" && ./xmlquery --value RUNDIR)
actual_archive=$(cd "$new_case" && ./xmlquery --value DOUT_S_ROOT)
if [[ "$actual_exeroot" != "$expected_exeroot" || "$actual_rundir" != "$expected_rundir" || "$actual_archive" != "$new_archive" ]]; then
    echo "Cloned case has unexpected output paths; archive has not been copied:" >&2
    (cd "$new_case" && ./xmlquery CASE CASEROOT EXEROOT RUNDIR DOUT_S_ROOT) >&2
    echo "Resolve these paths before using the new case." >&2
    exit 1
fi

# Copy into a unique staging directory in the same filesystem. If copying or
# renaming fails, the final archive path is not mistaken for a complete copy.
stage=$(mktemp -d "$archives/.${new}.copy.XXXXXXXX")
trap '[[ -z ${stage:-} ]] || rm -rf -- "$stage"' EXIT
echo "Copying archive; this may take time and use substantial space..."
cp -a --reflink=auto -- "$old_archive/." "$stage/"

# Rename file and directory basenames in the COPY, working from deepest paths
# upward so a renamed parent never invalidates a child pathname.
while IFS= read -r -d '' path; do
    name=${path##*/}
    target="${path%/*}/${name//$old/$new}"
    [[ ! -e "$target" && ! -L "$target" ]] || {
        echo "Name collision within copied archive: $target" >&2
        exit 1
    }
    mv -- "$path" "$target"
done < <(find "$stage" -depth -name "*$old*" -print0)

# rpointer.* are plain-text files naming restart files. Their copied contents
# must match the renamed restart filenames. The originals are not edited.
find "$stage" -type f -name 'rpointer.*' -exec sed -i "s/$old/$new/g" {} +

[[ ! -e "$new_archive" && ! -L "$new_archive" ]] || {
    echo "Destination appeared while copying: $new_archive" >&2
    exit 1
}
mv -T -- "$stage" "$new_archive"
stage=

echo "Done. Original and copy:"
du -sh "$old_archive" "$new_archive"
echo "Correctly named case: $new_case"
echo "Copied archive: $new_archive"
echo "Copied pathnames still containing the old name (should be empty):"
find "$new_archive" -name "*$old*" -print
echo "Symlinks in the copy pointing to the old name, if any:"
find "$new_archive" -type l -lname "*$old*" -print
