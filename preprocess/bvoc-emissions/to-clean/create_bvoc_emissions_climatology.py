#!/usr/bin/env python3
# Original idea: Sara Marie Blichner. Edited by Adele Zaini with ChatGPT.
"""Create year-2000 BVOC emission climatologies from NorESM CAM history files.

Workflow
--------
1. Find the history files for each requested year (both endpoints included).
2. Read the first source header to select coordinates and optional bounds.
3. Concatenate each year with NCO, then check its yearly time axis and metadata.
4. Remove the February 29 record block from source leap years, then rebuild
   every yearly time axis on the same 365-day reference year 2000.
5. Average corresponding grid cells and half-hourly slots across years.
6. Convert kg of emitted compound/m2/s to molecules/cm2/s.
7. Keep one emission field and its coordinates.
8. For Gregorian output, insert a synthetic February 29 copied from February 28
   and rebuild time, date, datesec and any time bounds. Save the final file.

Usage
-----
Load NCO in the terminal before starting Python:
    module load NCO/5.2.9-foss-2024a
    python create_bvoc_emissions_climatology.py CASE START_YEAR END_YEAR SFISOP --calendar noleap

Use SFMTERP instead of SFISOP for monoterpenes. Optional arguments:
    --history-field h1       CAM history stream (default: h1)
    --postfix _test          Suffix inserted into the output filename
    --path /archive         Parent directory containing CASE/atm/hist
    --output-path /output   Destination directory

Input and output
----------------
Input selection: ARCHIVE/CASE/atm/hist/CASE.cam.STREAM.YEAR*.nc.
Files are sorted by filename; timestamps must then form a complete year.
Output: ems_CASE_START-END_VARIABLE[POSTFIX][_addleapyear].nc.
Existing final output files are not overwritten.
Working files stay in OUTPUT/FINAL_FILENAME_WITHOUT_EXTENSION_work/.
Rerun the same command to resume: completed steps are reused; interrupted steps
are overwritten. A completion marker is written only after each step succeeds.
Changes to input sizes/mtime, arguments or PROCESSING_VERSION invalidate affected steps.
Completed years are skipped before opening NetCDF files; their metadata is cached.
Raw files are removed after alignment; intermediates are cleaned after final output.
For noleap sources, alignment moves the raw file instead of copying its flux array.
After an interruption during alignment, that year may need concatenating again.
Completion records from the two preceding checkpoint versions can be upgraded
when their raw files and markers are intact; this reads raw coordinates once.
This uses file metadata, not full-file checksums or repeated source-header reads.
Do not edit cached files or restore source files with unchanged sizes/mtime.
The empty work directory and its lock file remain after successful cleanup.
If you change scientific processing code, increment PROCESSING_VERSION below.

Python requires numpy, netCDF4 and cftime. Python reads headers and coordinates; NCO handles the large emission arrays. NCO can still require
substantial memory for yearly fields and temporary disk space for all years.

Calendar and sampling
---------------------
--calendar selects the OUTPUT calendar, not the source calendar:
    noleap:    365 days, 17,520 half-hourly records; no February 29.
    gregorian: 366 days, 17,568 records; reference year 2000 is a leap year.
Source calendars are read from the concatenated yearly files. Source February 29 is excluded before
averaging for either output choice. Gregorian output always uses a synthetic
February 29, even when the source period contains no leap years.

Accepted timestamps start at January 1 00:00 or 00:30 and repeat every 30 minutes.
The sampling phase must match across years. For the 00:30 phase, the final record
is January 1 00:00 of the following year. Records are grouped in 48-record day
blocks relative to that phase; this also defines the February slicing below.
The script rejects incomplete years, gaps and duplicate timestamps; it does not
fetch missing boundary records from adjacent filename years or resample data.

Flux-validation scope
---------------------
Full-array missing-value, NaN/infinity and mean-preservation checks are omitted.
Timestamp, calendar, grid and metadata checks remain because record slicing and
alignment depend on them. They run once per concatenated year, not per source
file. Time and optional bounds must use float64 storage, to retain half-hourly
precision when rewritten in days. Source files within a year must share units, calendar, packing and grid;
these per-file differences are no longer checked by Python. NCO command
failures still stop the script. Removing
flux scans reduces work but does not remove filesystem or conversion costs.

Scientific assumptions and CAM use
----------------------------------
Input is instantaneous flux on an unchanged (time, lat, lon) grid. A time: mean
or time: sum attribute is rejected, but absent metadata cannot prove that a
history stream was instantaneous: also check the producing case configuration.
Mass must be kg of compound, not kg of carbon. Generic kg/m2/s metadata alone
cannot establish that distinction; check the model's history-field calculation.

SFISOP/SFMTERP are total surface-flux diagnostics: in the inspected CTRL they
include interactive MEGAN plus prescribed biomass-burning emissions. Averaging
them does not isolate the vegetation contribution or retain interannual variation.

The inspected NorESM reader treats all 3-D variables as emission sectors and
sums them. This script therefore keeps exactly one 3-D flux field (ISOP or MTERP).
The receiving chemistry species is selected separately by srf_emis_specifier.
For the total-flux fBVOC approach, replace the original prescribed ISOP/MTERP
entries and disable their interactive contributions to avoid double counting.
The inspected reader also imposes an isoprene daily profile: bypass that extra
adjustment in the fBVOC case when prescribing this half-hourly climatology.
This script does not modify CAM; validate applied fluxes in a short model test.
"""

import argparse
import os
import re
import shutil
import subprocess
import hashlib
import json
import fcntl
from contextlib import contextmanager
from pathlib import Path

import cftime
import numpy as np
from netCDF4 import Dataset


# =============================================================================
# Defaults, physical constants and output variable names
# =============================================================================
DEFAULT_NORESM_ARCHIVE = "/cluster/work/users/adelez/archive"
DEFAULT_OUTPUT_PATH = "/cluster/projects/nn9188k/adelez/noresm-inputdata/processed/bvoc-emissions"
AVOGADRO = 6.022e23  # molecules / mol
MOLAR_MASS = {"SFISOP": 68.114200e-3, "SFMTERP": 136.228400e-3}  # kg / mol
TIMESTEPS_PER_DAY = 48
STEP_SECONDS = 86400 // TIMESTEPS_PER_DAY
TIME_UNITS = "days since 2000-01-01 00:00:00"

# CAM reads all 3-D variables as emission sectors.
# The receiving species is selected by srf_emis_specifier.
OUTPUT_VAR_NAME = {"SFISOP": "ISOP", "SFMTERP": "MTERP"}
PROCESSING_VERSION = "bvoc-2000-v2"  # Bump when calculations or metadata rules change.
# Exact hashes of the two preceding checkpoint scripts, for one-time migration.
LEGACY_SCRIPT_HASHES = ('8b0789f21dbe4752358d477feb1cf195c4c166cfcd19be2decb8b3bb55a85881', '19ff51c16073a4d7e9b63589fa87d2a567d16bfc65c8078edc8187e0a3378b86')
_WORK_LOCK_FD = None  # Inherited by NCO children while they write checkpoints.


# =============================================================================
# Utility functions
# =============================================================================


def run_command(command, files=None):
    """Run one NCO command and stop immediately if it fails.

    Pass argument lists directly (no shell). For multi-file operators, send
    absolute filenames through stdin to avoid shell command-length limits.
    NCO must already be available in the environment that launched Python."""
    print(f"  {command[0]}", flush=True)
    filenames = None if files is None else "".join(str(p.resolve()) + "\n" for p in files)
    subprocess.run(list(map(str, command)), input=filenames, text=True, check=True,
                   stdin=subprocess.DEVNULL if files is None else None,
                   pass_fds=() if _WORK_LOCK_FD is None else (_WORK_LOCK_FD,))


@contextmanager
def working_directory(folder):
    """Keep checkpoints across exits; prevent two runs writing the same folder.

    NCO children inherit the lock, so killing Python cannot admit another
    writer while its child is still running. The last process closing it releases it.
    Leave .lock in place: deleting it while a job runs would break exclusion.
    """
    global _WORK_LOCK_FD
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(f"Another process is using {folder}. Stop it before restarting.")
        previous, _WORK_LOCK_FD = _WORK_LOCK_FD, lock.fileno()
        try:
            yield
        finally:
            _WORK_LOCK_FD = previous
            # Close our descriptor via the context manager; do not explicitly
            # unlock the shared descriptor while an NCO child may still hold it.


def file_stamp(path):
    """Cheap identity check; does not open or scan a NetCDF file."""
    stat = path.stat()
    return [str(path.resolve()), stat.st_size, stat.st_mtime_ns]


def step_key(inputs, settings):
    """Fingerprint settings and input size/mtime without reading data arrays."""
    return hashlib.sha256(json.dumps(
        [settings, [file_stamp(p) for p in inputs]], sort_keys=True
    ).encode()).hexdigest()


def completed(output, key):
    """Return a matching completion record, or None for an unfinished step."""
    try:
        done = json.loads(output.with_suffix(".nc.done.json").read_text())
        if done["key"] == key and done["output"] == file_stamp(output):
            return done
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def mark_completed(output, key, info=None):
    """Commit a small completion record only after the output closes successfully."""
    marker = output.with_suffix(".nc.done.json")
    pending = marker.with_suffix(".tmp")
    pending.write_text(json.dumps({"key": key, "output": file_stamp(output), "info": info},
                                 default=lambda value: value.tolist()))
    pending.replace(marker)


def checkpoint(output, inputs, settings, action):
    """Reuse completed steps; replace incomplete outputs through a partial file.

    A yearly action also returns calendar/grid/bounds metadata. Saving it in the
    marker lets the next run skip the entire year without reopening its NetCDF.
    File size/mtime checks detect ordinary changes, not silent data corruption.
    """
    key = step_key(inputs, settings)
    done = completed(output, key)
    if done is not None:
        print(f"  reuse {output.name}", flush=True)
        return done.get("info")
    output.with_suffix(".nc.done.json").unlink(missing_ok=True)
    partial = output.with_suffix(".partial.nc")
    partial.unlink(missing_ok=True)
    print(f"  build {output.name}", flush=True)
    info = action(partial)
    partial.replace(output)
    mark_completed(output, key, info)
    return info


def aligned_metadata(raw, year, var):
    """Validate source coordinates once and remove leap-day bounds offsets."""
    info = check_year(raw, year, var)
    if info["leap"] and info["offsets"] is not None:
        info["offsets"] = np.concatenate([info["offsets"][:2832], info["offsets"][2880:]])
    return info


def upgrade_legacy(raw, aligned, files, settings, year, var):
    """Reuse old checkpoints only when their full input/output signatures match.

    Old yearly markers depend on the raw file. Verify that chain before replacing
    it with a marker that depends directly on the source files. No flux scan.
    Unrecognised or incomplete checkpoints are rebuilt, never trusted by name.
    """
    if completed(aligned, step_key(files, settings)) is not None or not raw.exists():
        return
    for script_hash in LEGACY_SCRIPT_HASHES:
        old_settings = [script_hash, *settings[1:]]
        if completed(raw, step_key(files, old_settings)) is None:
            continue
        if completed(aligned, step_key([raw], old_settings)) is not None:
            print(f"{year}: upgrading completed year (one metadata read)", flush=True)
            info = aligned_metadata(raw, year, var)
            mark_completed(aligned, step_key(files, settings), info)
        else:
            # Preserve a completed concatenation even if alignment was interrupted.
            mark_completed(raw, step_key(files, settings))
        return


def remove_intermediate(path):
    """Remove only this named intermediate and its own checkpoint/partial files."""
    for item in (path, path.with_suffix(".partial.nc"),
                 path.with_suffix(".nc.done.json"), path.with_suffix(".nc.done.tmp")):
        item.unlink(missing_ok=True)


def output_variable_name(var):
    """Return the readable NetCDF label for the selected history diagnostic.

    These labels are a convention; the inspected CAM reader discovers 3-D
    fields and receives the target chemistry species from the namelist."""
    return OUTPUT_VAR_NAME[var]


# =============================================================================
# Input validation: timestamps and metadata
# =============================================================================


def check_year(path, year, var):
    """Validate one concatenated yearly file before using fixed record indices.

    Read metadata and coordinates only; emission arrays are not validated.
    Require an unpacked (time, lat, lon) field and unlimited time.
    Decode timestamps using the yearly file's units and calendar; compare date and
    datesec when present. Verify complete, evenly spaced half-hourly coverage.

    Returns a dictionary with calendar, phase (0 or 1800 seconds), leap status,
    bounds variable name, bounds offsets in days relative to each timestamp,
    and a metadata/grid signature for cross-year comparisons. No bounds means
    offsets=None. Malformed or inconsistent input raises ValueError."""
    offsets = None
    with Dataset(path) as ds:
        flux, time = ds.variables[var], ds.variables["time"]
        if np.dtype(time.dtype).kind != "f" or np.dtype(time.dtype).itemsize != 8:
            raise ValueError(f"{path}: time must be float64 before rewriting half-hourly timestamps in days.")
        if flux.dimensions != ("time", "lat", "lon") or not ds.dimensions["time"].isunlimited():
            raise ValueError(f"{path}: expected (time,lat,lon) with unlimited time for ncrcat.")
        if any(k in flux.ncattrs() for k in ("scale_factor", "add_offset")):
            raise ValueError(f"{path}: unpack the flux before using ncrcat.")
        units = getattr(flux, "units", "")
        normalized = re.sub(r"[\s^*]", "", units.lower())
        description = " ".join(str(getattr(flux, k, "")) for k in ("long_name", "description", "comment"))
        if normalized not in {"kg/m2/s", "kgm-2s-1", "kgm-2/s", "kg/m2s"} or re.search(r"kg\s*c\b|as carbon|mass of carbon", description, re.I):
            raise ValueError(f"{path}: check compound-mass units: {units!r}; {description}")
        if re.search(r"time\s*:\s*(mean|sum)", getattr(flux, "cell_methods", "")):
            raise ValueError(f"{path}: this script expects instantaneous half-hourly output.")
        cal = getattr(time, "calendar", "").lower()
        cal = {"365_day": "noleap", "standard": "gregorian"}.get(cal, cal)
        if cal not in {"noleap", "gregorian", "proleptic_gregorian"}:
            raise ValueError(f"{path}: missing/unsupported source calendar {cal!r}.")
        bound_name = getattr(time, "bounds", "")
        grid = (np.asarray(ds.variables["lat"][:]), np.asarray(ds.variables["lon"][:]))
        signature = (cal, units, bound_name)
        reference = (signature, grid)
        print(f"{year}: source calendar={cal}, {var}:units={units}; {description}")
        origin = f"seconds since {year:04d}-01-01 00:00:00"
        dates = cftime.num2date(time[:], time.units, calendar=cal)
        sec = np.asarray(cftime.date2num(dates, origin, calendar=cal), dtype=float)
        if np.ma.getmaskarray(time[:]).any() or not np.isfinite(sec).all():
            raise ValueError(f"{path}: missing/nonfinite time values.")
        for key, expected in (("date", [d.year*10000 + d.month*100 + d.day for d in dates]),
                              ("datesec", [d.hour*3600 + d.minute*60 + d.second for d in dates])):
            if key in ds.variables and not np.array_equal(ds.variables[key][:], expected):
                raise ValueError(f"{path}: {key} disagrees with time.")
        if bound_name:
            b = ds.variables[bound_name]
            if np.dtype(b.dtype).kind != "f" or np.dtype(b.dtype).itemsize != 8:
                raise ValueError(f"{path}: time bounds must be float64 before rewriting in days.")
            if b.dimensions[0] != "time" or b.shape != (len(sec), 2):
                raise ValueError(f"{path}: expected time bounds shaped (time,2).")
            bd = cftime.num2date(b[:].ravel(), getattr(b, "units", time.units), calendar=cal)
            bs = np.asarray(cftime.date2num(bd, origin, calendar=cal)).reshape(-1, 2)
            if np.ma.getmaskarray(b[:]).any() or not np.isfinite(bs).all() or np.any(bs[:, 1] < bs[:, 0]):
                raise ValueError(f"{path}: invalid time bounds.")
            offsets = (bs - sec[:, None]) / 86400.
    days = (cftime.datetime(year+1, 1, 1, calendar=cal) - cftime.datetime(year, 1, 1, calendar=cal)).days
    phase = float(sec[0]) if len(sec) else -1
    if len(sec) != days*TIMESTEPS_PER_DAY or not -1e-3 <= phase <= STEP_SECONDS+1e-3 or not np.allclose(
        sec, phase + np.arange(len(sec))*STEP_SECONDS, rtol=0, atol=1e-3
    ):
        raise ValueError(f"{year}: expected {days*TIMESTEPS_PER_DAY} consecutive half-hourly records "
                         "starting Jan 1 00:00 or 00:30. Check gaps, duplicates and year boundaries.")
    if not (abs(phase) < 1e-3 or abs(phase-STEP_SECONDS) < 1e-3):
        raise ValueError(f"{year}: unexpected sampling phase {phase} seconds.")
    return dict(calendar=cal, phase=round(phase), leap=(days == 366), bounds=reference[0][2],
                offsets=offsets, signature=reference)


# =============================================================================
# NCO workflow steps
# =============================================================================


def concatenate_yearly_files(files, var, outfile):
    """Concatenate one year's sorted files along time using ncrcat.

    Keep only the requested flux, time, horizontal coordinates and optional
    time bounds. Retain existing date/datesec for later in-place updates. -6 requests 64-bit-offset NetCDF3;
    -C prevents automatic inclusion of associated variables."""
    # Inspect one header only; NCO itself reads all source files.
    with Dataset(files[0]) as ds:
        bound_name = getattr(ds.variables["time"], "bounds", "")
        fields = [var, "time", "lat", "lon"] + ([bound_name] if bound_name else [])
        fields += [key for key in ("date", "datesec") if key in ds.variables]
    run_command(["ncrcat", "-O", "-6", "-C", "-v", ",".join(fields), "-o", outfile], files)


def remove_feb29_from_leap_years(infile, outfile):
    # these original 1-based indices are used only AFTER the time checks.
    """Remove the leap-day record block from a validated half-hourly year.

    NCO -F uses inclusive, 1-based indexing:
        January-February 28: 1..2832      (59 * 48 records)
        February 29:        2833..2880   (48 records, removed)
        March-December:     2881..17568
    With phase=1800, each day block ends at midnight on the following date.
    --msa_usr_rdr preserves the requested order of the two retained slices."""
    run_command(["ncks", "-O", "-6", "-F", "--msa_usr_rdr", "-d", "time,1,2832",
                 "-d", "time,2881,17568", infile, outfile])


def rebuild_time(file, calendar_type, phase, bound_name, offsets):
    # rebuild numeric time, date, datesec AND any bounds consistently.
    """Write consistent year-2000 time coordinates while preserving phase.

    file is edited in place. calendar_type determines date decoding; phase is
    seconds after January 1 midnight. Numeric time is rebuilt in days since
    2000-01-01, then date (YYYYMMDD) and datesec (seconds since midnight) follow
    from it. Changing the units attribute alone would not move timestamps.
    If present, bounds are reconstructed using their original offsets in days.
    The emission values are not modified."""
    with Dataset(file, "r+") as ds:
        n = len(ds.dimensions["time"])
        values = (phase + np.arange(n)*STEP_SECONDS) / 86400.
        dates = cftime.num2date(values, TIME_UNITS, calendar=calendar_type)
        time = ds.variables["time"]
        time[:] = values
        time.units, time.calendar = TIME_UNITS, calendar_type
        for key, values in (("date", [d.year*10000 + d.month*100 + d.day for d in dates]),
                            ("datesec", [d.hour*3600 + d.minute*60 + d.second for d in dates])):
            variable = ds.variables[key] if key in ds.variables else ds.createVariable(key, "i4", ("time",))
            variable[:] = values
        ds.variables["date"].long_name = "current date (YYYYMMDD)"
        ds.variables["datesec"].units = "seconds"
        if bound_name:
            ds.variables[bound_name][:] = time[:][:, None] + offsets
            ds.variables[bound_name].units = TIME_UNITS
            ds.variables[bound_name].calendar = calendar_type


def average_yearly_files(files, outfile):
    # nces is the current name of ncea; yearly time axes have already been aligned.
    """Average aligned yearly arrays element by element with nces (ncea).

    Every input has 365 days and the same reference time axis. Each source
    year receives equal weight; the seasonal and half-hourly cycles remain."""
    run_command(["nces", "-O", "-6", "-o", outfile], files)


def convert_units_and_update_metadata(infile, outfile, var, name):
    """Convert compound mass flux to molecular flux with ncap2.

    molecules/cm2/s = kg/m2/s * (molecules/mol) / (kg/mol) * 1e-4.
    The 1e-4 factor converts the per-m2 denominator to per-cm2. Arithmetic uses
    double precision, then stores the new flux as float32. The original field
    remains in this intermediate file until save_emission_variables removes it.
    No conversion from carbon mass is implemented."""
    factor = AVOGADRO / MOLAR_MASS[var] * 1e-4
    run_command(["ncap2", "-O", "-6", "-s", f"{name}=float(double({var})*{factor:.17g});", infile, outfile])
    run_command(["ncatted", "-O", "-a", f"units,{name},o,c,molecules/cm2/s",
                 "-a", f"long_name,{name},o,c,Prescribed {var} emission climatology", outfile])


def save_emission_variables(infile, outfile, name, bound_name):
    """Extract the single converted flux and the forcing time/grid variables.

    This is required for CAM: keeping the original and converted 3-D fields
    would make the inspected reader sum both as emission sectors. Coordinate
    vectors and optional (time, 2) bounds are not 3-D emission sectors."""
    fields = [name, "time", "date", "datesec", "lat", "lon"] + ([bound_name] if bound_name else [])
    run_command(["ncks", "-O", "-6", "-C", "-v", ",".join(fields), infile, outfile])


def add_synthetic_feb29(infile, outfile, phase, bound_name, offsets, tmp):
    # year 2000 is Gregorian-leap even if NO source year was a leap year.
    """Build Gregorian year 2000 by copying the February 28 day block.

    From a validated 365-day file, concatenate January-February 28, a second
    copy of February 28, and March-December. Shift time and bounds by one day
    in the copied and later blocks; then rebuild all time/date coordinates.
    Copy matching bounds offsets too. Source leap-day observations are not
    used: the added day is synthetic, so the 366-day annual mean may differ
    from the 365-day mean. No annual-total renormalization is applied."""
    pieces = []
    for label, first, last in (("before", 1, 2832), ("leap", 2785, 2832), ("after", 2833, 17520)):
        piece = tmp / f"{label}.nc"
        run_command(["ncks", "-O", "-6", "-F", "-d", f"time,{first},{last}", infile, piece])
        if label != "before":
            # advance synthetic Feb 29 and March-December, including bounds.
            with Dataset(piece, "r+") as ds:
                for key in ["time"] + ([bound_name] if bound_name else []):
                    ds.variables[key][:] = ds.variables[key][:] + 1.
        pieces.append(piece)
    run_command(["ncrcat", "-O", "-6", "-o", outfile], pieces)
    new_offsets = np.concatenate([offsets[:2832], offsets[2784:2832], offsets[2832:]]) if offsets is not None else None
    rebuild_time(outfile, "gregorian", phase, bound_name, new_offsets)


# =============================================================================
# Main workflow
# =============================================================================


def main(case_name, startyear, endyear, var, calendar_type, history_field="h1", postfix="",
         path=DEFAULT_NORESM_ARCHIVE, output_path=DEFAULT_OUTPUT_PATH):
    """Run the complete workflow and return the final NetCDF Path.

    Process startyear..endyear inclusively, one species per invocation.
    Temporary yearly files are aligned before averaging. The full-array flux
    checks and mean-preservation check are deliberately omitted to reduce I/O.
    Missing/nonfinite emission values are not rejected by this script; missing
    samples may affect the averaging weights used by NCO.
    Publish the final filename after all processing commands succeed."""
    if not 1 <= startyear <= endyear:
        raise ValueError("Invalid year range.")
    for program in ("ncrcat", "ncks", "nces", "ncap2", "ncatted"):
        if not shutil.which(program):
            raise ValueError("Load NCO first: module load NCO/5.2.9-foss-2024a")
    # 1. Resolve input/output paths and refuse to overwrite an existing result.
    name = output_variable_name(var)
    input_path = Path(path).expanduser() / case_name / "atm" / "hist"
    output_path = Path(output_path).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    suffix = "_addleapyear" if calendar_type == "gregorian" else ""
    final = output_path / f"ems_{case_name}_{startyear}-{endyear}_{var}{postfix}{suffix}.nc"
    if final.exists():
        raise ValueError(f"Output already exists: {final}. Move it or use --postfix.")
    print("Conversion assumes kg of emitted compound/m2/s; confirm this from the printed metadata/model.")
    tmp = output_path / (final.stem + "_work")
    # Explicit processing version: comment/documentation edits do not force a rebuild.
    settings = [PROCESSING_VERSION,
                case_name, startyear, endyear, var, calendar_type, history_field,
                postfix, str(input_path.resolve())]
    print(f"Working directory: {tmp}", flush=True)
    with working_directory(tmp):
        yearly, reference = [], None
        for year in range(startyear, endyear+1):
            files = sorted(input_path.glob(f"{case_name}.cam.{history_field}.{year:04d}*.nc"))
            if not files:
                raise ValueError(f"No history files for {year} in {input_path}.")
            # 2. Check the aligned checkpoint FIRST, before opening any NetCDF.
            raw, aligned = tmp / f"{year}_raw.nc", tmp / f"{year}.nc"
            upgrade_legacy(raw, aligned, files, settings, year, var)

            def prepare_year(out):
                print(f"{year}: concatenating {len(files)} files", flush=True)
                checkpoint(raw, files, settings,
                           lambda target: concatenate_yearly_files(files, var, target))
                print(f"{year}: checking yearly time axis", flush=True)
                info = aligned_metadata(raw, year, var)
                # 3. Move noleap data, avoiding an extra full-file copy. The raw
                # marker must disappear before its data can be modified in place.
                print(f"{year}: aligning time coordinates", flush=True)
                if info["leap"]:
                    remove_feb29_from_leap_years(raw, out)
                else:
                    raw.with_suffix(".nc.done.json").unlink(missing_ok=True)
                    raw.replace(out)
                rebuild_time(out, "noleap", info["phase"], info["bounds"], info["offsets"])
                return info

            info = checkpoint(aligned, files, settings, prepare_year)
            # Markers load JSON lists; normalise bounds for comparisons/slicing.
            if info["offsets"] is not None:
                info["offsets"] = np.asarray(info["offsets"])
            remove_intermediate(raw)
            # 4. Match grids/phases/bounds, then align the reference-year axis.
            if reference is not None:
                same_bounds = (info["offsets"] is None and reference["offsets"] is None) or (
                    info["offsets"] is not None and reference["offsets"] is not None and
                    np.allclose(info["offsets"], reference["offsets"], rtol=0, atol=1e-8))
                if info["phase"] != reference["phase"] or tuple(info["signature"][0]) != tuple(reference["signature"][0]) or not same_bounds or any(
                    not np.array_equal(a, b) for a, b in zip(info["signature"][1], reference["signature"][1])
                ):
                    raise ValueError("Sampling phase, grid, calendar, units or bounds differ between years.")
            reference = info
            yearly.append(aligned)
        avg, converted, saved = tmp / "average.nc", tmp / "converted.nc", tmp / "emissions.nc"
        # 5. Average matching half-hourly slots, convert units, keep one flux.
        checkpoint(avg, yearly, settings, lambda out: average_yearly_files(yearly, out))
        checkpoint(converted, [avg], settings,
                   lambda out: convert_units_and_update_metadata(avg, out, var, name))
        checkpoint(saved, [converted], settings,
                   lambda out: save_emission_variables(converted, out, name, reference["bounds"]))
        # 6. Add a synthetic leap day only for Gregorian year-2000 output.
        if calendar_type == "gregorian":
            leap = tmp / "emissions_leap.nc"
            checkpoint(leap, [saved], settings,
                       lambda out: add_synthetic_feb29(saved, out, reference["phase"],
                                                      reference["bounds"], reference["offsets"], tmp))
            saved = leap
        # 7. Publish atomically, keeping the completed checkpoint for later reuse.
        # The work directory and final file share a filesystem; a hard link avoids
        # another large copy and refuses to overwrite an existing final result.
        os.link(saved, final)
        # 8. Only after final publication succeeds, remove known intermediates.
        for item in yearly + [tmp / f"{year}_raw.nc" for year in range(startyear, endyear+1)] + [
            avg, converted, tmp / "emissions.nc", tmp / "emissions_leap.nc",
            tmp / "before.nc", tmp / "leap.nc", tmp / "after.nc"
        ]:
            remove_intermediate(item)
    print(f"Final file: {final}")
    return final


# =============================================================================
# Command-line interface
# =============================================================================


def parse_args():
    """Parse the case, inclusive year range, species and output calendar.

    Archive/output defaults are defined below the module documentation.
    --help displays the workflow, assumptions and available options."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("case_name")
    parser.add_argument("startyear", type=int)
    parser.add_argument("endyear", type=int)
    parser.add_argument("var", choices=OUTPUT_VAR_NAME)
    parser.add_argument("--calendar", dest="calendar_type", required=True, choices=["noleap", "gregorian"], help="Output calendar (reference year 2000)")
    parser.add_argument("--history-field", default="h1")
    parser.add_argument("--postfix", default="")
    parser.add_argument("--path", default=DEFAULT_NORESM_ARCHIVE)
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    try:
        main(**vars(parse_args()))
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"ERROR: {exc}")
