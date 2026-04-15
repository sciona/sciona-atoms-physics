from __future__ import annotations

from typing import Any

import icontract
import numpy as np

from sciona.ghost.registry import register_atom

from .witnesses import witness_find_fof_clusters


@register_atom(witness_find_fof_clusters)
@icontract.require(lambda x: x is not None, "x cannot be None")
@icontract.require(lambda b: b is not None, "b cannot be None")
@icontract.require(lambda L: L is not None, "L cannot be None")
@icontract.ensure(lambda result: result is not None, "find_fof_clusters output must not be None")
def find_fof_clusters(
    x: np.ndarray,
    b: float,
    L: float,
    mode: str = "precompute",
    max_neighbors: int | None = None,
    batch_size: int | None = None,
) -> np.ndarray:
    """Compute periodic friends-of-friends cluster labels for a point cloud."""
    from scipy.spatial import cKDTree

    n = x.shape[0]
    if n == 0:
        return np.array([], dtype=np.intp)

    if mode == "periodic" and L > 0:
        tree = cKDTree(x, boxsize=L)
    else:
        tree = cKDTree(x)

    pairs = tree.query_pairs(r=b, output_type="ndarray")
    labels = np.arange(n, dtype=np.intp)

    def find(i: int) -> int:
        while labels[i] != i:
            labels[i] = labels[labels[i]]
            i = labels[i]
        return i

    def union(a: int, c: int) -> None:
        ra, rc = find(a), find(c)
        if ra != rc:
            labels[ra] = rc

    for i, j in pairs:
        union(int(i), int(j))

    for i in range(n):
        labels[i] = find(i)
    return labels
