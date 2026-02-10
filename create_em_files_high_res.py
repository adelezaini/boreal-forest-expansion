# Author: Sara Marie Blichner

# Note: This is a copy of MASTERS/create_em_files_high_res.py with added documentation
# NOTE: correct the input years removeing the first year od spinup (2007 -> 2008)

#!/usr/bin/env python3

# -*- coding: utf-8 -*-

#   Create high-resolution emission files from NORESM CAM history files:
#   - Outputs files with emissions in molec/cm2/s for isoprene and monoterpene.
#   - Handles leap years by removing Feb 29th data.
#   - Changes date to year 2000 for compatibility with other input data.
#   - Requires NCO (NetCDF Operators) to be installed and loaded.
#   - "high-resolution" here means daily data for each day of the year (365 days) - fincl2 ='SFisoprene','SFmonoterp' (daily resolution in CAM history files).

#   Usage example:
#   python create_em_files_high_res.py case_name startyear endyear var [history_field] [postfix] [path] [output_path]   
#   where var is either 'SFisoprene' or 'SFmonoterp'.
#   history_field defaults to 'h1'.
#   postfix defaults to ''.
#   path defaults to path_to_noresm_archive.
#   output_path defaults to outpath_default.

#   Example:
#   python3 create_em_files_high_res.py CTRL_2000_sec_nudg_f19_f19 2008 2013 SFisoprene h1 /cluster/home/adelez/storage/archive /cluster/home/adelez/noresm-inputdata/BVOCfromCTRL
#  Note: Adjust paths and module load commands as needed for your system.


from subprocess import run
import numpy as np
import pathlib
from pathlib import Path

# Default settings
path_to_noresm_archive = '/cluster/home/adelez/storage/archive' #'/proj/bolinc/users/x_sarbl/noresm_archive'
outpath_default = '/cluster/home/adelez/noresm-inputdata/BVOCfromCTRL' #'/proj/bolinc/users/x_sarbl/noresm_input_data'

# How to load nco on your system
load_nco_string = 'module load NCO/5.0.3-intel-2021b' #module load NCO/4.6.3-nsc1'

"""
Example usage: 
python create_em_files_high_res.py case_name 2015 2018 SFisoprene h2 /proj/bolinc/users/x_sarbl/noresm_archive /proj/bolinc/users/x_sarbl/noresm_input_data 

python3 create_em_files_high_res.py CTRL_2000_sec_nudg_f19_f19 2007 2013 [SFisoprene/SFmonoterp
] h1 /cluster/home/adelez/storage/archive /cluster/home/adelez/noresm-inputdata/BVOCfromCTRL
"""

Av = 6.022e23  # Avogadro's number
M_iso = 68.114200e-3  # Molar mass isoprene kg/mol
M_mono = 136.228400e-3  # Molar mass monoterpene kg/mol
path_this_file = str(pathlib.Path().absolute()) 

# Output chemistry variable name mapping:
# SFisoprene -> ISOP
# SFmonoterp -> H10H16
var_dic = dict(SFmonoterp='H10H16',
               SFisoprene='ISOP')

# Molar masses for conversion:
# SFisoprene: 68.114200e-3 kg/mol
# SFmonoterp: 136.228400e-3 kg/mol
M_dic = dict(SFmonoterp=M_mono,
             SFisoprene=M_iso)

def main(case_name, startyear, endyear, var,
         history_field='h1',
         postfix='',
         path=path_to_noresm_archive,
         output_path=outpath_default
         ):
    """
    Create high-resolution emission files from NORESM CAM history files.
    
    Arguments:
    - case_name: Name of the NORESM case. E.g., 'CTRL_2000_sec_nudg_f19_f19'.
    - startyear: Starting year for processing (inclusive).  E.g., 2008.
    - endyear: Ending year for processing (inclusive). E.g., 2013.
    - var: Variable to process. Either 'SFisoprene' or 'SFmonoterp'.
    - history_field: CAM history field to use (default 'h1').   
    - postfix: Postfix to add to output filenames (default ''). E.g., '_addleapyear'.
    """
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  1. Define input and output paths
    path = Path(path)
    path = Path(path)
    output_path = Path(output_path)
    input_path = path / case_name / 'atm' / 'hist'
    # -> ex: .../CASE/atm/hist/CASE.cam.h1.2007-01-01-00000.nc
    startyear = int(startyear)
    endyear = int(endyear)
    # Create list to hold all nco commands to run
    comms = []

    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  2. Loop over years — create yearly emission files
    #   by concatenating CAM history files for the year

    for y in range(startyear, endyear + 1):
        print(y)
        #  Get all CAM history files for year y
        filenames = str(input_path) + f'/{case_name}.cam.{history_field}.{y:04.0f}*.nc'
        # Example: filenames = 'CASE.cam.h1.2007*.nc'
        print(filenames)
        # Define output temporary file for the year
        outfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}.nc'
        # Example: outfile   = 'tmp_CASE_2007_SFisoprene.nc'
        # Extract date, datesec, and emission variable into yearly file
        co = f'ncrcat -O -v date,datesec,{var} {filenames} {outfile}'
        # Example command:
        # ncrcat -O -v date,datesec,SFisoprene CASE.cam.h1.2007*.nc tmp_CASE_2007_SFisoprene.nc
        
        # Append command to list:
        comms.append(co)

    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  3. Handle leap years by removing Feb 29th data for each year that is a leap year (divisible by 4)
    #  to ensure consistent 365-day years across all years.

    #   For each leap year:
    #   - Move original yearly file to a temp file
    #   - Extract data up to Feb 28th into slice1
    #   - Extract data from Mar 1st onward into slice2
    #   - Adjust time in slice2 to remove the leap day
    #   - Concatenate slice1 and adjusted slice2 back into the temp file
    #   - Move temp file back to original yearly file name
    
    for y in range(startyear, endyear + 1):
        # Check if year is a leap year
        if y in np.arange(0, 2100, 4): # Logic: if year divisible by 4
            print(f'{y} is leap year')
            outfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}.nc'
            tmpfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp.nc'
            tmpfile_slice1 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice1.nc'
            tmpfile_slice2 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice2.nc'
            tmpfile_slice3 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice3.nc'

            # Move original file to temp file
            co = f'mv {outfile} {tmpfile}'
            comms.append(co)
            # Extract days until Feb 28th (time indices 1 to 2832)
            co = f'ncks -O -F -d time,1,2832 {tmpfile} {tmpfile_slice1}'
            comms.append(co)
            # Extract days from Mar 1st onward (time indices 2881 to 17568)
            co = f'ncks -O -F -d time,2881,17568 {tmpfile} {tmpfile_slice2}'
            comms.append(co)
            # Adjust time in slice2 to remove leap day (decrease all times by 1) & save to slice3
            co = f'ncap2  -O -s "time=time-1."  {tmpfile_slice2}  {tmpfile_slice3}'
            comms.append(co)
            # Concatenate slice1 and adjusted slice3 back into temp file
            co = f'ncrcat -O {tmpfile_slice1} {tmpfile_slice3} {tmpfile}'
            comms.append(co)
            # Move temp file back to original yearly file name
            co = f'mv {tmpfile} {outfile}'
            comms.append(co)

    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  4. Compute average emissions over all years
    #   by averaging the yearly files created above into a single file.
    #   The output file will contain average emissions for each day of the year.
    #   This is done using ncea to compute the ensemble average.

    infiles = str(output_path) + f'/tmp_{case_name}_*_{var}.nc'
    # Example: infiles = 'tmp_CASE_*_SFisoprene.nc'
    outfile = output_path / f'avg_{case_name}_{startyear}-{endyear}_{var}.nc'
    # Example: outfile = 'avg_CASE_2008-2013_SFisoprene.nc'

    # Perform ensemble average over yearly files
    co = f'ncea -O {infiles} {outfile}'
    comms.append(co)
    # Example command:
    # ncea -O tmp_CASE_*_SFisoprene.nc avg_CASE_2008-2013_SFisoprene.nc 

    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  5. Convert emissions to molec/cm2/s and adjust date to year 2000
    #   - Change file format to NetCDF3
    #   - Convert emissions from kg/m2/s to molec/cm2/s
    #   - Adjust date variable to year 2000 for compatibility
    #   - Update variable attributes for units
    #   - Save final variables to new output file

    # Change format to NetCDF3
    co = f'ncks -3 -O {outfile} {outfile}'
    comms.append(co)

    new_var = var_dic[var]
    M_var = M_dic[var]
    # Convert emissions to molec/cm2/s
    co = f'ncap2 -A -s "{new_var}={var}*{Av}/{M_var}*1e-4" {outfile}' #-O
    # Example command:
    # ncap2 -A -s "ISOP = SFisoprene [kg/m2/s]
    #                      * 6.022e23 [kg/mol] -> mol/m2/s
    #                      / 68.114200e-3 [molecules/mol] -> molecules/m2/s
    #                      * 1e-4" -> molecules/cm2/s
    #                       avg_CASE_2008-2013_SFisoprene.nc
    comms.append(co)
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  6. Adjust date variable to year 2000 for compatibility
    #  Required because NorESM expects emissions defined in year 2000 regardless of actual simulation years.
    
    #  - Calculate difference in years from 2000
    # different months have different dates and require different corrections
    diff = (startyear - 2000) * 10000 # Calculate difference in date format YYYYMMDD (e.g., 20080101 - 20000101 = 80000)
    #  - Adjust date variable accordingly
    if diff > 0:
        co = f'ncap2 -A -s "date=date-{diff}."  {outfile}' #-O  # E.g., for 2008, subtract 80000
    else:
        co = f'ncap2 -A -s "date=date+{-diff}."  {outfile}' #-O # E.g., for 1998, add 20000
    comms.append(co)
    # Update variable attributes for units
    co = f'ncatted -a units,{new_var},o,c,molecules/cm2/s {outfile}' # E.g., ISOP -> molecules/cm2/s
    comms.append(co)
    co = f'ncatted -a units,time,o,c,"days since 2000-01-01 00:00:00" {outfile}' # E.g., time -> days since 2000-01-01
    comms.append(co)
    # Save a clean output file (only date, new_var, datesec)
    final_file = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc'
    co = f'ncks -O -v date,{new_var},datesec {outfile} {final_file}'
    comms.append(co)
    # Run all commands
    for co in comms:
        print(co)
        run(f'{load_nco_string} &&' + co, shell=True)
        # txt = input("Type something to test this out: ")
        # print(f"Is this what you just said? {txt}")
    # Finally add extra days:
    comms = add_extra_day(case_name,
                          startyear, endyear, output_path, var,
                          postfix)      
    for co in comms:
        print(co)
        run(f'{load_nco_string} &&' + co, shell=True)   


def add_extra_day(case_name,
                  startyear, endyear, output_path, var,
                  postfix):
    """
    Put the 29th of February back in the emission files.
    Logic: copies 28th feb and inserts as 29th feb

    Some chemistry setups require leap days, others require no leap days.
    This script prepares both versions.
    """

    comms = []
    infile = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc'
    final_file = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}_addleapyear.nc' #Example: ems_CASE_2008-2013_SFisoprene_addleapyear.nc

    tmpfile_slice1 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice1.nc'
    tmpfile_slice2 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice2.nc'
    tmpfile_slice3 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice3.nc'
    tmpfile = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp.nc'

    # Extract data up to Feb 28th (time indices 1 to 2832)
    co = f'ncks -O -F -d time,1,2832 {infile} {tmpfile_slice1}'
    comms.append(co)
    # Extract data from Feb 29th to Dec 31st (time indices 2833 to 17520)
    co = f'ncks -O -F -d time,2833,17520 {infile} {tmpfile_slice2}'
    comms.append(co)
    # Adjust time in slice2 to add the leap day (increase all times by 1)
    co = f'ncap2  -O -s "time=time+1."  {tmpfile_slice2}  {tmpfile_slice2}'
    comms.append(co)
    # Extract only Feb 29th data (time indices 2833 to 2881)
    co = f'ncks -O -F -d time,2833,2881 {infile} {tmpfile_slice3}'
    comms.append(co)
    # Adjust date in slice3 to add the leap day (increase date by 229 to account for Feb 29th)
    co = f'ncap2  -O -s "date=date-301+229"  {tmpfile_slice3}  {tmpfile_slice3}'

    comms.append(co)
    # Concatenate slice1, slice3 (Feb 29th), and adjusted slice2 back into final file
    co = f'ncrcat -O {tmpfile_slice1} {tmpfile_slice3} {tmpfile_slice2} {final_file}'
    comms.append(co)

    return comms

if __name__ == '__main__':
    import sys

    args = sys.argv
    main(*args[1:])
