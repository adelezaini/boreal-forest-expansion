"""Raw NorESM history files -> one processed netCDF file per category.

Steps (in this order):
  1. find the history files; check every file for the requested variables
     (a variable present in only some files is an error)
  2. open them, keeping only the requested variables
  3. validate the time axis: contiguous monthly means (no gaps, duplicates,
     instantaneous or non-monthly tapes)
  4. fix the time axis (model writes interval END -> use the interval midpoint)
  5. drop the spin-up months
  6. correct wrong unit labels (no numeric changes; data stay in model units)
  7. add secondary variables for the requested categories (error if inputs are missing)
  8. save one file per category: <alias>_<component>_<category>_<y0>-<y1>.nc

Changes vs the old code (old: postprocess.py main(): create_dataset -> fix_units -> fix_ds
-> Ghan -> save_postprocessed)
--------------------------------------------------------------------------------------
- CHANGED the unit conversion step is gone (model units kept; see units.py).
- CHANGED secondary variables are computed only for the categories being processed
          (old: fix_ds always needed cb_SOA_NA, AREL, FREQL, T, U, V ... and crashed with
          an unhelpful KeyError if any was missing, e.g. with vars='BVOC').
- CHANGED spin-up is still dropped here (default 12 months), right after the time fix,
          and recorded in the output attribute `spinup_months_dropped`.
- ADDED   (review round 2) step 1 checks all files, not only the first; step 3 validates
          the time axis before any record is dropped; step 7 raises a clear error when a
          requested category lacks the inputs of its secondary variables.
"""
import logging

from . import derived, fileio, variables

log = logging.getLogger(__name__)


def run(casename, alias, component, raw_path, out_path,
        tape="h0", categories=None, spinup_months=12, skip_existing=False):
    """Postprocess one case and component. Returns the list of written files.

    skip_existing : skip categories whose output file already exists in `out_path`.
    """
    categories = categories or list(variables.CATEGORIES[component])
    if skip_existing:
        done = [c for c in categories if fileio.processed_exists(out_path, alias, component, c)]
        if done:
            log.info("Already processed, skipped: %s", ", ".join(done))
        categories = [c for c in categories if c not in done]
        if not categories:
            return []
    wanted = variables.variables_for(component, categories)

    files = fileio.find_history_files(raw_path, casename, component, tape)
    ds, missing = fileio.open_history(files, wanted)
    ds = fileio.validate_monthly_means(ds)
    ds = fileio.fix_time(ds)
    ds = fileio.drop_spinup(ds, spinup_months)
    # Read everything once into memory: otherwise every category (and every derived
    # variable) re-reads the history files lazily through dask, which is very slow.
    ds = ds.load()
    ds = fileio.fix_unit_labels(ds, variables.UNIT_LABEL_FIXES[component])
    ds, added = derived.add_derived(ds, component, categories)

    provenance = {
        "casename": casename, "alias": alias, "component": component, "tape": tape,
        "spinup_months_dropped": spinup_months, "n_history_files": len(files),
        "missing_variables": ", ".join(missing) or "none",
        "processing": "boreal_forest_expansion.postprocess; time = midpoint of time bounds; "
                      "model units kept",
    }
    written = []
    for cat in categories:
        cat_vars = (variables.ALWAYS_INCLUDE[component]
                    + variables.CATEGORIES[component][cat] + added.get(cat, []))
        written.append(fileio.save_category(ds, cat_vars, out_path, alias, component, cat, provenance))
    return written
