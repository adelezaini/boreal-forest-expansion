"""Analysis of the boreal LCC experiment (step 1: Ghan decomposition; D1 far-field check).

Modules
  loading         open monthly CAM output (time fix, spin-up drop, annual means)
  ghan            Ghan (2013) terms, SW / LW / net, downward positive
  regions         area weights, latitude bands, modified-cell mask
  stats           paired yearly statistics, cell-wise t-test, FDR
  farfield        D1: far-field check of the BVOC contrast
  farfield_plots  D1 figures
  megan           MEGAN compounds -> CAM species, formulas, OH rate constants (chem_mech.in)
  emissions       D2: MEGAN emission budget (others vs ISOP+MTERP), from CLM MEG_*
  emissions_plots D2 figures
"""
