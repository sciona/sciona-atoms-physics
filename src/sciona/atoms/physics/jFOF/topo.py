from __future__ import annotations

from typing import TypeAlias

import icontract
import numpy as np

from ageoa.ghost.registry import register_atom

from .topo_witnesses import witness_topological_loss_computation

Array: TypeAlias = np.ndarray
Scalar: TypeAlias = float


@register_atom(witness_topological_loss_computation)
@icontract.require(lambda tau: isinstance(tau, (float, int, np.number)), "tau must be numeric")
@icontract.ensure(lambda result: result is not None, "topological_loss_computation output must not be None")
def topological_loss_computation(
    key: Array,
    logits: Array,
    pos32: Array,
    nbr_idx: Array,
    b: Array,
    max_iters: int,
    tau: float,
) -> Scalar:
    """Compute a topological loss measuring local cluster consistency."""
    logits_arr = np.asarray(logits, dtype=np.float64)
    nbr = np.asarray(nbr_idx, dtype=np.intp)

    n = logits_arr.shape[0]
    probs = np.exp(logits_arr / tau)
    probs = probs / (probs.sum(axis=-1, keepdims=True) + 1e-15)

    loss = 0.0
    for i in range(min(n, max_iters)):
        neighbor_count = nbr.shape[1] if nbr.ndim > 1 else 1
        for j_idx in range(neighbor_count):
            j = int(nbr[i, j_idx]) if nbr.ndim > 1 else int(nbr[i])
            if 0 <= j < n:
                loss += float(-np.sum(probs[i] * np.log(probs[j] + 1e-15)))
    return float(loss / max(n, 1))
