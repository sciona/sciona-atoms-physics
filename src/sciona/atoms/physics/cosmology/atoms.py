"""Cosmological flux correction atoms.

Implements K-correction for astronomical flux measurements to normalize
observed photometry to rest-frame values accounting for cosmological redshift.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

import icontract
from sciona.ghost.registry import register_atom

from .witnesses import witness_flux_k_correction


@register_atom(witness_flux_k_correction)
@icontract.require(lambda flux: np.all(np.isfinite(flux)), "Flux must be finite")
@icontract.require(lambda redshift: np.all(redshift >= 0), "Redshift must be non-negative")
@icontract.ensure(lambda result: np.all(np.isfinite(result)), "Corrected flux must be finite")
def flux_k_correction(
    flux: NDArray[np.float64],
    redshift: NDArray[np.float64],
    band_index: int = 0,
) -> NDArray[np.float64]:
    """Apply K-correction to astronomical flux measurements.

    Corrects observed flux for cosmological redshift effects to normalize
    measurements to rest-frame values. Uses the (1+z) scaling approximation
    for broadband photometry.

    flux_corrected = flux * (1 + z)
    """
    _ = band_index
    return flux * (1.0 + redshift)
