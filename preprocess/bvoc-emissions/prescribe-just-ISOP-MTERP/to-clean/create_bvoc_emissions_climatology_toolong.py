#!/usr/bin/env python3

# Original idea: Sara Marie Blichner. Edited by Adele Zaini with ChatGPT.
"""Create year-2000 BVOC emission climatologies from NorESM CAM history files.

Workflow
--------
1. Find the history files for each requested year (both endpoints included).
2. Check the source calendar, grid, units and complete half-hourly time axis.
3. Concatenate each year with NCO and reject missing or nonfinite flux values.
4. Remove the February 29 record block from source leap years, then rebuild
   every yearly time axis on the same 365-day reference year 2000.
5. Average corresponding grid cells and half-hourly slots across years.
6. Convert kg of emitted compound/m2/s to molecules/cm2/s.
7. Keep one emission field and its coordinates; verify mean-flux preservation.
8. For Gregorian output, insert a synthetic February 29 copied from February 28
   and rebuild time, date, datesec and any time bounds. Save the final file.

Usage
-----
module load NCO/5.2.9-foss-2024a
python create_bvoc_emissions_climatology.py CASE START_YEAR END_YEAR SFISOP/SFMTERP --calendar noleap

Optional arguments:
    --history-field h1       CAM history stream (default: h1)
    --postfix _test          Suffix inserted into the output filename
    --path /archive         Parent directory containing CASE/atm/hist
    --output-path /output   Destination directory
    
--calendar selects the OUTPUT calendar, not the source calendar:
    noleap:    365 days, 17,520 half-hourly records; no February 29.
    gregorian: 366 days, 17,568 records; reference year 2000 is a leap year.
Source calendars are read from the files. Source February 29 is excluded before
averaging for either output choice. Gregorian output always uses a synthetic
February 29, even when the source period contains no leap years.

----------------------------------
Output: ems_CASE_START-END_VARIABLE[POSTFIX][_addleapyear].nc.
Existing output files are not overwritten. Temporary files are removed on exit.

Python requires numpy, netCDF4 and cftime. Python reads headers, coordinates and
scalar checks; NCO handles the large emission arrays. NCO can still require
substantial memory for yearly fields and temporary disk space for all years.


CAM use
----------------------------------
- Mass must be kg of compound, not kg of carbon. Generic kg/m2/s metadata alone cannot establish that distinction; check the model's history-field calculation.

- SFISOP/SFMTERP are total surface-flux diagnostics: in the inspected CTRL they include interactive MEGAN plus prescribed biomass-burning emissions. For the total-flux fBVOC approach, replace the original prescribed ISOP/MTERP entries and disable their interactive contributions to avoid double counting.

- The inspected reader also imposes an isoprene daily profile: bypass that extra adjustment in the fBVOC case when prescribing this half-hourly climatology. This script does not modify CAM; validate applied fluxes in a short model test.

- Input is instantaneous flux on an unchanged (time, lat, lon) grid. The inspected NorESM reader treats all 3-D variables as emission sectors and sums them. This script therefore keeps exactly one 3-D flux field (ISOP or MTERP). The receiving chemistry species is selected separately by srf_emis_specifier.


Updates since the previous version (after this version)
---------------------------------
- Fixed working directory and checkpoints to resume interrupted runs.
- Completed years skipped without reopening their NetCDF files.
- Incomplete or outdated intermediates rebuilt automatically.
- Completed work retained after interruption; intermediates cleaned after success.
- Folder locking prevents concurrent writers, including surviving NCO children.
- Float64 time/bounds required to prevent precision loss when rewriting timestamps.
- Compatible checkpoints from the two preceding versions can be upgraded.

Scientific calculations and command-line usage are unchanged.
"""

import argparse
import re
import shutil
import subprocess
import tempfile
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

OUTPUT_VAR_NAME = {"SFISOP": "ISOP", "SFMTERP": "MTERP"}
# "MTERP" or "C10H16"?
# CAM reads all 3-D variables as emission sectors.
# The receiving species is selected by srf_emis_specifier.


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
                   stdin=subprocess.DEVNULL if files is None else None)


def output_variable_name(var):
    """Return the readable NetCDF label for the selected history diagnostic.

    These labels are a convention; the inspected CAM reader discovers 3-D
    fields and receives the target chemistry species from the namelist."""
    return OUTPUT_VAR_NAME[var]


# =============================================================================
# Input validation: timestamps, metadata and emission values
# =============================================================================


def check_year(files, year, var):
    """Validate one source year before using fixed record indices.

    Read metadata and coordinates only; check_flux later checks emission data.
    Require an unpacked (time, lat, lon) field and unlimited time for ncrcat.
    Decode timestamps using each file's units and calendar; compare date and
    datesec when present. Verify complete, evenly spaced half-hourly coverage.

    Returns a dictionary with calendar, phase (0 or 1800 seconds), leap status,
    bounds variable name, bounds offsets in days relative to each timestamp,
    and a metadata/grid signature for cross-year comparisons. No bounds means
    offsets=None. Malformed or inconsistent input raises ValueError."""
    seconds, bounds = [], []
    reference = None
    for path in files:
        with Dataset(path) as ds:
            flux, time = ds.variables[var], ds.variables["time"]
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
            if reference is None:
                reference = (signature, grid)
                print(f"{year}: source calendar={cal}, {var}:units={units}; {description}")
            elif signature != reference[0] or any(not np.array_equal(a, b) for a, b in zip(grid, reference[1])):
                raise ValueError(f"{path}: calendar, units, bounds or grid changed within year.")
            origin = f"seconds since {year:04d}-01-01 00:00:00"
            dates = cftime.num2date(time[:], time.units, calendar=cal)
            sec = np.asarray(cftime.date2num(dates, origin, calendar=cal), dtype=float)
            if np.ma.getmaskarray(time[:]).any() or not np.isfinite(sec).all():
                raise ValueError(f"{path}: missing/nonfinite time values.")
            for key, expected in (("date", [d.year*10000 + d.month*100 + d.day for d in dates]),
                                  ("datesec", [d.hour*3600 + d.minute*60 + d.second for d in dates])):
                if key in ds.variables and not np.array_equal(ds.variables[key][:], expected):
                    raise ValueError(f"{path}: {key} disagrees with time.")
            seconds.append(sec)
            if bound_name:
                b = ds.variables[bound_name]
                if b.dimensions[0] != "time" or b.shape != (len(sec), 2):
                    raise ValueError(f"{path}: expected time bounds shaped (time,2).")
                bd = cftime.num2date(b[:].ravel(), getattr(b, "units", time.units), calendar=cal)
                bs = np.asarray(cftime.date2num(bd, origin, calendar=cal)).reshape(-1, 2)
                if np.ma.getmaskarray(b[:]).any() or not np.isfinite(bs).all() or np.any(bs[:, 1] < bs[:, 0]):
                    raise ValueError(f"{path}: invalid time bounds.")
                bounds.append((bs - sec[:, None]) / 86400.)
    sec = np.concatenate(seconds)
    cal = reference[0][0]
    days = (cftime.datetime(year+1, 1, 1, calendar=cal) - cftime.datetime(year, 1, 1, calendar=cal)).days
    phase = float(sec[0]) if len(sec) else -1
    if len(sec) != days*TIMESTEPS_PER_DAY or not 0 <= phase <= STEP_SECONDS or not np.allclose(
        sec, phase + np.arange(len(sec))*STEP_SECONDS, rtol=0, atol=1e-3
    ):
        raise ValueError(f"{year}: expected {days*TIMESTEPS_PER_DAY} consecutive half-hourly records "
                         "starting Jan 1 00:00 or 00:30. Check gaps, duplicates and year boundaries.")
    if not (abs(phase) < 1e-3 or abs(phase-STEP_SECONDS) < 1e-3):
        raise ValueError(f"{year}: unexpected sampling phase {phase} seconds.")
    return dict(calendar=cal, phase=round(phase), leap=(days == 366), bounds=reference[0][2],
                offsets=np.concatenate(bounds) if bounds else None, signature=reference)


def check_flux(file, var, stats_file):
    """Reject missing/nonfinite emissions and return the unweighted array mean.

    NCO computes scalar counts, extrema and a mean; Python reads only scalars.
    Check both _FillValue and missing_value explicitly. Remove missing-value
    masking from the temporary RAM variable only, so sentinel comparisons work;
    retain the original variable's missing count. The source file is unchanged.
    NaNs are detected by f != f; nonfinite extrema/means also reject infinities.
    Finite negative values are not rejected by this check."""
    with Dataset(file) as ds:
        field = ds.variables[var]
        sentinels = []
        for attr in ("_FillValue", "missing_value"):
            if attr in field.ncattrs():
                sentinels.extend(np.atleast_1d(field.getncattr(attr)).astype(float))
    script = f"*f=double({var}); missing_count={var}.number_miss(); f.delete_miss(); sentinel_count=0.; "
    for value in set(sentinels):
        if np.isfinite(value):
            script += f"sentinel_count=sentinel_count+(f=={value:.17g}).total(); "
    script += "nan_count=(f!=f).total(); minimum_flux=f.min(); maximum_flux=f.max(); mean_flux=f.avg();"
    run_command(["ncap2", "-O", "-6", "-v", "-s", script, file, stats_file])
    keys = ("missing_count", "sentinel_count", "nan_count", "minimum_flux", "maximum_flux", "mean_flux")
    with Dataset(stats_file) as ds:
        values = [float(np.ma.asarray(ds.variables[k][...], dtype=float).filled(np.nan)) for k in keys]
    if not np.isfinite(values).all() or any(v != 0 for v in values[:3]):
        raise ValueError(f"{file}: {var} contains missing or nonfinite flux values: {dict(zip(keys, values))}")
    return values[-1]


# =============================================================================
# NCO workflow steps
# =============================================================================


def concatenate_yearly_files(files, var, info, outfile):
    """Concatenate one year's sorted files along time using ncrcat,retaining date fields for later in-place updates.

    Keep only the requested flux, time, horizontal coordinates and optional
    time bounds. Rebuild date/datesec later. -6 requests 64-bit-offset NetCDF3;
    -C prevents automatic inclusion of associated variables."""
    # Preserve existing date variables to avoid adding them to a large NetCDF3 file.
    fields = [var, "time", "date", "datesec", "lat", "lon"]
    if info["bounds"]:
        fields.append(info["bounds"])
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
    Temporary yearly files are aligned before averaging. Check flux validity
    before averaging so missing samples cannot silently change the weights.
    Compare input and converted-output means on the same 365-day sample set,
    before adding any synthetic leap day. This scalar check is not a spatial
    comparison or an area-weighted global-emissions budget.
    Publish the final filename only after these processing checks succeed."""
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
    with tempfile.TemporaryDirectory(prefix="bvoc_", dir=output_path) as folder:
        tmp, yearly, reference = Path(folder), [], None
        yearly_means = []
        stats_file = tmp / "flux_checks.nc"
        for year in range(startyear, endyear+1):
            files = sorted(input_path.glob(f"{case_name}.cam.{history_field}.{year:04d}*.nc"))
            if not files:
                raise ValueError(f"No history files for {year} in {input_path}.")
            # 2. Validate timestamps; concatenate and check the full source year.
            info = check_year(files, year, var)
            raw, aligned = tmp / f"{year}_raw.nc", tmp / f"{year}.nc"
            concatenate_yearly_files(files, var, info, raw)
            source_mean = check_flux(raw, var, stats_file)
            # 3. Remove the leap-day block so every year has the same 365-day sequence.
            if info["leap"]:
                remove_feb29_from_leap_years(raw, aligned)
                raw.unlink()
                source_mean = check_flux(aligned, var, stats_file)
                if info["offsets"] is not None:
                    info["offsets"] = np.concatenate([info["offsets"][:2832], info["offsets"][2880:]])
            else:
                raw.rename(aligned)
            # 4. Match grids/phases/bounds, then align the reference-year axis.
            if reference is not None:
                same_bounds = (info["offsets"] is None and reference["offsets"] is None) or (
                    info["offsets"] is not None and reference["offsets"] is not None and
                    np.allclose(info["offsets"], reference["offsets"], rtol=0, atol=1e-8))
                if info["phase"] != reference["phase"] or info["signature"][0] != reference["signature"][0] or not same_bounds or any(
                    not np.array_equal(a, b) for a, b in zip(info["signature"][1], reference["signature"][1])
                ):
                    raise ValueError("Sampling phase, grid, calendar, units or bounds differ between years.")
            reference = info
            rebuild_time(aligned, "noleap", info["phase"], info["bounds"], info["offsets"])
            yearly.append(aligned)
            yearly_means.append(source_mean)
        avg, converted, saved = tmp / "average.nc", tmp / "converted.nc", tmp / "emissions.nc"
        # 5. Average matching half-hourly slots, convert units, keep one flux.
        average_yearly_files(yearly, avg)
        convert_units_and_update_metadata(avg, converted, var, name)
        save_emission_variables(converted, saved, name, reference["bounds"])
        # compare the same 365-day sample set before adding synthetic Feb 29.
        # This is an unweighted grid/time mean, not an area-weighted global total.
        # 6. Verify mean preservation, allowing for float32 output rounding.
        expected_mean = float(np.mean(yearly_means))
        recovered_mean = check_flux(saved, name, stats_file) / (AVOGADRO / MOLAR_MASS[var] * 1e-4)
        if not np.isclose(recovered_mean, expected_mean, rtol=2e-6, atol=1e-30):
            raise ValueError(f"Mean-flux check failed: input={expected_mean:.12g}, output={recovered_mean:.12g} kg/m2/s")
        print(f"Mean-flux check passed: input={expected_mean:.12g}, output={recovered_mean:.12g} kg/m2/s")
        # 7. Add a synthetic leap day only for Gregorian year-2000 output.
        if calendar_type == "gregorian":
            leap = tmp / "emissions_leap.nc"
            add_synthetic_feb29(saved, leap, reference["phase"], reference["bounds"], reference["offsets"], tmp)
            saved = leap
        # 8. Move the checked result out of the temporary directory.
        saved.rename(final)
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
