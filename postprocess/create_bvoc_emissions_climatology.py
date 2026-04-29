#!/usr/bin/env python3

# Original idea of the script - author: Sara Marie Blichner
# Edited by Adele Zaini with ChatGPT

"""
Create BVOC emission climatology files from NorESM atmospheric -h1- history output.

The script:
1. Concatenates monthly NorESM output into yearly files.
2. Optionally removes Feb 29 from leap years before averaging.
3. Averages emissions across years.
4. Converts emissions from kg/m2/s to molecules/cm2/s.
5. Resets dates to reference year 2000.
6. Saves a final emission file.
7. If a leap year was present, adds a synthetic Feb 29 by duplicating Feb 28.

Important:
This script assumes 48 timesteps per day, i.e. 30-minute output.
It uses NCO commands rather than loading the full NetCDF data into Python -> quicker and more memory efficient for large files.

Usage:
    python create_bvoc_emissions_climatology.py NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-test_20260428-diagnostics-3yr \
     2007 2013 SFisoprene \
     --calendar noleap \
     --history-field h1 \
     --postfix _test \
     --path /cluster/work/users/adelez/archive \
     --output-path /cluster/projects/nn9188k/adelez/noresm-inputdata/bvoc-emissions  

The calendar must be specified explicitly:
--calendar noleap: assumes all years have 365 days. 
    Feb 29 is never removed or added.
--calendar gregorian: assumes leap years contain Feb 29. 
    Feb 29 is removed from leap years before averaging.
    After averaging, a synthetic Feb 29 is added by duplicating Feb 28.
"""


from pathlib import Path
from subprocess import run
import argparse
import calendar
import shlex


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_NORESM_ARCHIVE = "/cluster/work/users/adelez/archive"
DEFAULT_OUTPUT_PATH = "/cluster/projects/nn9188k/adelez/noresm-inputdata/bvoc-emissions"

LOAD_NCO_STRING = "module load NCO/5.2.9-foss-2024a"

# =============================================================================
# Physical constants and variable mappings
# =============================================================================

AVOGADRO = 6.022e23  # molecules / mol

MOLAR_MASS = {
    "SFisoprene": 68.114200e-3,   # kg / mol
    "SFmonoterp": 136.228400e-3,  # kg / mol
}

OUTPUT_VAR_NAME = {
    "SFisoprene": "ISOP",
    "SFmonoterp": "H10H16",
}


# =============================================================================
# Time-axis assumptions
# =============================================================================
# Assumption: 48 timesteps per day.
# With NCO -F, indexing is 1-based.
#
# For 48 timesteps/day:
#   Jan 1 through Feb 28 = 59 days * 48 = 2832 timesteps
#   Feb 29 = timesteps 2833-2880 in a leap year
#   Mar 1 starts at timestep 2881 in a leap year
#   365-day year = 17520 timesteps
#   366-day year = 17568 timesteps

TIMESTEPS_PER_DAY = 48

FEB_28_END = 59 * TIMESTEPS_PER_DAY                  # 2832
FEB_28_START = FEB_28_END + 1                        # 2833

MAR_1_START_LEAP = 60 * TIMESTEPS_PER_DAY + 1        # 2881
LEAP_YEAR_END = 366 * TIMESTEPS_PER_DAY              # 17568
NOLEAP_YEAR_END = 365 * TIMESTEPS_PER_DAY            # 17520

FEB_29_END = FEB_28_START + TIMESTEPS_PER_DAY - 1    # 2880


# =============================================================================
# Utility functions
# =============================================================================

def quote(value):
    """
    Quote a value for safe use in shell commands.
    """
    return shlex.quote(str(value))


def run_command(command):
    """
    Run one shell command.

    check=True makes the script stop immediately if an NCO command fails.
    """
    full_command = f"{LOAD_NCO_STRING} && {command}"
    print(full_command)
    run(full_command, shell=True, check=True)


def validate_inputs(case_name, startyear, endyear, var, path, output_path):
    """
    Validate user inputs before running expensive operations.
    """
    if startyear > endyear:
        raise ValueError("startyear must be smaller than or equal to endyear")

    if var not in OUTPUT_VAR_NAME:
        valid = ", ".join(OUTPUT_VAR_NAME)
        raise ValueError(f"Unknown variable '{var}'. Valid choices are: {valid}")

    archive_path = Path(path)

    if not archive_path.exists():
        raise FileNotFoundError(f"NorESM archive path does not exist: {archive_path}")

    input_path = archive_path / case_name / "atm" / "hist"

    if not input_path.exists():
        raise FileNotFoundError(f"Input history path does not exist: {input_path}")

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    return input_path, output_path


def leap_years_in_range(startyear, endyear):
    """
    Return Gregorian leap years in the selected period.
    """
    return [
        year
        for year in range(startyear, endyear + 1)
        if calendar.isleap(year)
    ]


# =============================================================================
# NCO workflow steps
# =============================================================================

def concatenate_yearly_files(
    case_name,
    startyear,
    endyear,
    var,
    history_field,
    input_path,
    output_path,
):
    """
    Concatenate monthly NorESM history files into one temporary file per year.

    Input files are expected to follow the pattern:
        <case_name>.cam.<history_field>.<year>*.nc
    """
    commands = []

    for year in range(startyear, endyear + 1):
        pattern = input_path / f"{case_name}.cam.{history_field}.{year:04d}*.nc"
        outfile = output_path / f"tmp_{case_name}_{year:04d}_{var}.nc"

        commands.append(
            f"ncrcat -O "
            f"-v date,datesec,{var} "
            f"{quote(pattern)} "
            f"{quote(outfile)}"
        )

    return commands


def remove_feb29_from_leap_years(
    case_name,
    startyear,
    endyear,
    var,
    output_path,
):
    """
    Remove Feb 29 from Gregorian leap years.

    This is only used when --calendar gregorian.

    The reason for removing Feb 29 before averaging is that all years must have
    the same length for a clean day-by-day climatological average.
    """
    commands = []

    for year in leap_years_in_range(startyear, endyear):
        print(f"{year}: removing Feb 29 before averaging")

        yearly_file = output_path / f"tmp_{case_name}_{year:04d}_{var}.nc"
        tmp_file = output_path / f"tmp_{case_name}_{year:04d}_{var}_without_feb29_tmp.nc"

        before_feb29 = output_path / f"tmp_{case_name}_{year:04d}_{var}_before_feb29.nc"
        after_feb29 = output_path / f"tmp_{case_name}_{year:04d}_{var}_after_feb29.nc"
        after_feb29_shifted = output_path / f"tmp_{case_name}_{year:04d}_{var}_after_feb29_shifted.nc"

        commands.extend([
            # Move original yearly file to a temporary file.
            f"mv {quote(yearly_file)} {quote(tmp_file)}",

            # Keep Jan 1 through Feb 28.
            f"ncks -O -F -d time,1,{FEB_28_END} "
            f"{quote(tmp_file)} {quote(before_feb29)}",

            # Keep Mar 1 through Dec 31, skipping Feb 29.
            f"ncks -O -F -d time,{MAR_1_START_LEAP},{LEAP_YEAR_END} "
            f"{quote(tmp_file)} {quote(after_feb29)}",

            # Shift the remaining time coordinate back by one day.
            f'ncap2 -O -s "time=time-1." '
            f"{quote(after_feb29)} {quote(after_feb29_shifted)}",

            # Recombine into a 365-day file.
            f"ncrcat -O "
            f"{quote(before_feb29)} "
            f"{quote(after_feb29_shifted)} "
            f"{quote(tmp_file)}",

            # Restore original yearly filename.
            f"mv {quote(tmp_file)} {quote(yearly_file)}",
        ])

    return commands


def average_yearly_files(case_name, startyear, endyear, var, output_path):
    """
    Average all yearly temporary files into one multi-year climatology file.
    """
    infiles = output_path / f"tmp_{case_name}_*_{var}.nc"
    avg_file = output_path / f"avg_{case_name}_{startyear}-{endyear}_{var}.nc"

    commands = [
        f"ncea -O {quote(infiles)} {quote(avg_file)}",

        # Keep original behavior: convert to NetCDF3.
        f"ncks -3 -O {quote(avg_file)} {quote(avg_file)}",
    ]

    return commands, avg_file


def convert_units_and_update_metadata(avg_file, startyear, var):
    """
    Convert emission units and update metadata.

    Original variables are assumed to be in kg/m2/s.

    Conversion:
        kg/m2/s
        * (1 / kg_per_mol)
        * molecules_per_mol
        * 1e-4

    The factor 1e-4 converts from per m2 to per cm2.
    """
    commands = []

    new_var = OUTPUT_VAR_NAME[var]
    molar_mass = MOLAR_MASS[var]

    commands.append(
        f'ncap2 -A -s "{new_var}={var}*{AVOGADRO}/{molar_mass}*1e-4" '
        f"{quote(avg_file)}"
    )

    # Re-reference date values to year 2000.
    # Example:
    #   2007 dates become 2000 dates by subtracting 70000.
    date_offset = (startyear - 2000) * 10000

    if date_offset > 0:
        commands.append(
            f'ncap2 -A -s "date=date-{date_offset}." '
            f"{quote(avg_file)}"
        )
    else:
        commands.append(
            f'ncap2 -A -s "date=date+{-date_offset}." '
            f"{quote(avg_file)}"
        )

    commands.extend([
        f"ncatted -a units,{new_var},o,c,molecules/cm2/s "
        f"{quote(avg_file)}",

        f'ncatted -a units,time,o,c,"days since 2000-01-01 00:00:00" '
        f"{quote(avg_file)}",
    ])

    return commands


def save_emission_variables(
    case_name,
    startyear,
    endyear,
    var,
    postfix,
    output_path,
    avg_file,
):
    """
    Save only the variables needed in the final emission file.
    """
    new_var = OUTPUT_VAR_NAME[var]

    final_file = output_path / (
        f"ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc"
    )

    commands = [
        f"ncks -O -v date,{new_var},datesec "
        f"{quote(avg_file)} {quote(final_file)}"
    ]

    return commands, final_file


def add_synthetic_feb29(
    case_name,
    startyear,
    endyear,
    var,
    postfix,
    output_path,
):
    """
    Add a synthetic Feb 29 to the averaged final file.

    This is only used when --calendar gregorian and the selected period contains
    at least one leap year.

    Scientific note:
    The synthetic Feb 29 is produced by copying Feb 28. It is not an independent
    climatological average of actual Feb 29 values.
    """
    print("Adding synthetic Feb 29 by duplicating Feb 28")

    infile = output_path / (
        f"ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc"
    )

    final_file = output_path / (
        f"ems_{case_name}_{startyear}-{endyear}_{var}{postfix}_addleapyear.nc"
    )

    before_feb29 = output_path / (
        f"tmp_{case_name}_{startyear}-{endyear}_{var}_before_feb29.nc"
    )
    after_feb29 = output_path / (
        f"tmp_{case_name}_{startyear}-{endyear}_{var}_after_feb29.nc"
    )
    synthetic_feb29 = output_path / (
        f"tmp_{case_name}_{startyear}-{endyear}_{var}_synthetic_feb29.nc"
    )

    commands = [
        # Keep Jan 1 through Feb 28.
        f"ncks -O -F -d time,1,{FEB_28_END} "
        f"{quote(infile)} {quote(before_feb29)}",

        # Keep the rest of the no-leap climatology.
        f"ncks -O -F -d time,{FEB_28_START},{NOLEAP_YEAR_END} "
        f"{quote(infile)} {quote(after_feb29)}",

        # Shift the rest of the year forward by one day.
        f'ncap2 -O -s "time=time+1." '
        f"{quote(after_feb29)} {quote(after_feb29)}",

        # Copy Feb 28 to use as synthetic Feb 29.
        f"ncks -O -F -d time,{FEB_28_START},{FEB_29_END} "
        f"{quote(infile)} {quote(synthetic_feb29)}",

        # Change copied Feb 28 date values into Feb 29.
        # This follows the original script logic.
        f'ncap2 -O -s "date=date-301+229" '
        f"{quote(synthetic_feb29)} {quote(synthetic_feb29)}",

        # Concatenate:
        # Jan 1-Feb 28 + synthetic Feb 29 + shifted Mar 1-Dec 31.
        f"ncrcat -O "
        f"{quote(before_feb29)} "
        f"{quote(synthetic_feb29)} "
        f"{quote(after_feb29)} "
        f"{quote(final_file)}",
    ]

    return commands, final_file


# =============================================================================
# Main workflow
# =============================================================================

def main(
    case_name,
    startyear,
    endyear,
    var,
    calendar_type,
    history_field="h1",
    postfix="",
    path=DEFAULT_NORESM_ARCHIVE,
    output_path=DEFAULT_OUTPUT_PATH,
):
    """
    Run the full emission climatology workflow.
    """
    input_path, output_path = validate_inputs(
        case_name=case_name,
        startyear=startyear,
        endyear=endyear,
        var=var,
        path=path,
        output_path=output_path,
    )

    leap_years = leap_years_in_range(startyear, endyear)

    print("Configuration")
    print("-------------")
    print(f"Case name:       {case_name}")
    print(f"Years:           {startyear}-{endyear}")
    print(f"Variable:        {var}")
    print(f"History field:   {history_field}")
    print(f"Calendar:        {calendar_type}")
    print(f"Input path:      {input_path}")
    print(f"Output path:     {output_path}")

    if calendar_type == "gregorian":
        print(f"Gregorian leap years in period: {leap_years}")
    else:
        print("No-leap calendar selected: Feb 29 will not be removed or added")

    commands = []

    commands += concatenate_yearly_files(
        case_name=case_name,
        startyear=startyear,
        endyear=endyear,
        var=var,
        history_field=history_field,
        input_path=input_path,
        output_path=output_path,
    )

    if calendar_type == "gregorian" and leap_years:
        commands += remove_feb29_from_leap_years(
            case_name=case_name,
            startyear=startyear,
            endyear=endyear,
            var=var,
            output_path=output_path,
        )
    elif calendar_type == "gregorian" and not leap_years:
        print("Gregorian calendar selected, but no leap years are in the period.")
        print("Skipping Feb 29 removal and synthetic Feb 29 creation.")

    average_commands, avg_file = average_yearly_files(
        case_name=case_name,
        startyear=startyear,
        endyear=endyear,
        var=var,
        output_path=output_path,
    )
    commands += average_commands

    commands += convert_units_and_update_metadata(
        avg_file=avg_file,
        startyear=startyear,
        var=var,
    )

    save_commands, final_file = save_emission_variables(
        case_name=case_name,
        startyear=startyear,
        endyear=endyear,
        var=var,
        postfix=postfix,
        output_path=output_path,
        avg_file=avg_file,
    )
    commands += save_commands

    for command in commands:
        run_command(command)

    if calendar_type == "gregorian" and leap_years:
        leap_commands, leap_final_file = add_synthetic_feb29(
            case_name=case_name,
            startyear=startyear,
            endyear=endyear,
            var=var,
            postfix=postfix,
            output_path=output_path,
        )

        for command in leap_commands:
            run_command(command)

        print(f"Final file: {leap_final_file}")
    else:
        print(f"Final file: {final_file}")


# =============================================================================
# Command-line interface
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create averaged BVOC emission climatology files from NorESM "
            "atmospheric history output."
        )
    )

    parser.add_argument(
        "case_name",
        help="NorESM case name",
    )

    parser.add_argument(
        "startyear",
        type=int,
        help="First year included in the average",
    )

    parser.add_argument(
        "endyear",
        type=int,
        help="Last year included in the average",
    )

    parser.add_argument(
        "var",
        choices=OUTPUT_VAR_NAME.keys(),
        help="Emission variable to process",
    )

    parser.add_argument(
        "--calendar",
        required=True,
        choices=["noleap", "gregorian"],
        help=(
            "Calendar handling. Use 'noleap' if files do not contain Feb 29. "
            "Use 'gregorian' if leap years contain Feb 29."
        ),
    )

    parser.add_argument(
        "--history-field",
        default="h1",
        help="CAM history stream, e.g. h1 or h2. Default: h1",
    )

    parser.add_argument(
        "--postfix",
        default="",
        help="Optional postfix added to the output filename",
    )

    parser.add_argument(
        "--path",
        default=DEFAULT_NORESM_ARCHIVE,
        help="Path to the NorESM archive",
    )

    parser.add_argument(
        "--output-path",
        default=DEFAULT_OUTPUT_PATH,
        help="Directory where output files are written",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    main(
        case_name=args.case_name,
        startyear=args.startyear,
        endyear=args.endyear,
        var=args.var,
        calendar_type=args.calendar,
        history_field=args.history_field,
        postfix=args.postfix,
        path=args.path,
        output_path=args.output_path,
    )