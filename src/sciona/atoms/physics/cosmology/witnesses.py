"""Ghost witnesses for cosmology atoms."""

from __future__ import annotations

from sciona.ghost.abstract import AbstractArray


def witness_flux_k_correction(
    flux: AbstractArray,
    redshift: AbstractArray,
    band_index: int = 0,
) -> AbstractArray:
    """Ghost witness for K-correction of astronomical flux.

    Takes flux and redshift arrays and returns a corrected flux array
    of the same shape.
    """
    return flux
