"""Signed vector selection, adapted from edwinst/trackml_solution (BSD-2-Clause).

License: ../particle_tracking/source_tracking/solution_LICENSE.source.
"""
import numpy as np
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete finite vector matrices required')


@register_atom(concrete_only)
def select_by_absolute_inner_product(reference: np.ndarray, first: np.ndarray,
                                     second: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Select and orient one of two vectors by absolute inner product.

Inputs are aligned finite float64 matrices (N,D), D>=1. Empty batches are
allowed. Choose first only when its absolute inner product with reference is
strictly larger; ties choose second. Negate the selected vector if its inner
product is negative, leaving zero unchanged. Return the oriented vector (N,D)
and nonnegative inner product (N,). Inputs are not modified. No normalization:
this is an angular closest-axis rule only for equal-length candidates. Zero
vectors are allowed. Caller owns units; no confidence score or domain policy
is supplied. Nonfinite inner products reject before selection can hide them.
"""
    ref = np.asarray(reference)
    if ref.ndim != 2 or ref.shape[1] < 1:
        raise ValueError('Vector matrix (N,D), D>=1 required')
    arrays = [ref,np.asarray(first),np.asarray(second)]
    if any(a.dtype != np.float64 or a.shape != ref.shape or not np.isfinite(a).all() for a in arrays):
        raise ValueError('Aligned finite float64 vector matrices required')
    a,b = arrays[1:]
    with np.errstate(over='ignore',invalid='ignore'):
        left = np.einsum('ij,ij->i',ref,a)
        right = np.einsum('ij,ij->i',ref,b)
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError('Nonfinite inner product arithmetic')
    choose_first = np.abs(left) > np.abs(right)
    selected = np.where(choose_first[:,None],a,b)
    inner = np.where(choose_first,left,right)
    backwards = inner < 0
    selected[backwards,:] *= -1
    inner[backwards] *= -1
    return selected,inner
