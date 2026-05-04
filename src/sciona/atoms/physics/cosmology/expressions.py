"""Symbolic expressions for cosmological photometry corrections."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, METER, WATT


flux, redshift, corrected_flux, band_index = sp.symbols(
    "flux redshift corrected_flux band_index"
)

PHOTOMETRIC_FLUX = WATT.divide(METER.power(2))

COSMOLOGY_BIBLIOGRAPHY = [
    "hogg2002distance",
    "repo_sciona_atoms_physics",
]

FLUX_K_CORRECTION_EXPR = sp.Eq(corrected_flux, flux * (1 + redshift))
FLUX_K_CORRECTION_DIM_MAP = {
    "flux": PHOTOMETRIC_FLUX,
    "redshift": DIMENSIONLESS,
    "band_index": DIMENSIONLESS,
    "corrected_flux": PHOTOMETRIC_FLUX,
}
FLUX_K_CORRECTION_VARIABLES = {
    "flux": "input",
    "redshift": "input",
    "band_index": "parameter",
    "corrected_flux": "output",
}
FLUX_K_CORRECTION_VALIDITY_BOUNDS = {
    "redshift": (0.0, None),
    "band_index": (0.0, None),
}
