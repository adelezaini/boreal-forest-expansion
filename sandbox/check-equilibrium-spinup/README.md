Trying to run a python script as a job with sbatch,
```
sbatch create_cam-spinup_dataset.sh
```
but the compute node cannot see that directory at all:

in `create_cam_spinup_dataset.log_1498087.txt`:

```
path exists: False
[...]
FileNotFoundError: No files found for pattern: /nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/NF2000norbc_tropstratchem_spinup_f19_f19/atm/hist/NF2000norbc_tropstratchem_spinup_f19_f19.cam.h0.*.nc
```
