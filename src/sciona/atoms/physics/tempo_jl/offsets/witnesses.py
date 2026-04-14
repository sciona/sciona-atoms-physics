"""Witnesses for grouped Tempo.jl offset atoms."""

from __future__ import annotations

from typing import Any

from sciona.ghost.abstract import AbstractArray, AbstractScalar


def _offset_output(seconds: Any) -> AbstractArray | AbstractScalar:
    if isinstance(seconds, AbstractArray):
        return AbstractArray(shape=seconds.shape, dtype="float64")
    if isinstance(seconds, AbstractScalar):
        return AbstractScalar(dtype="float64")
    raise ValueError("Tempo offset witnesses require AbstractArray or AbstractScalar input")


def witness_offset_tt2tdb(seconds: Any) -> AbstractArray | AbstractScalar:
    """Low-order offset preserves scalar-vs-array shape semantics."""

    return _offset_output(seconds)


def witness_offset_tt2tdbh(seconds: Any) -> AbstractArray | AbstractScalar:
    """High-order offset preserves scalar-vs-array shape semantics."""

    return _offset_output(seconds)


def witness_tt2tdb_offset(seconds: Any) -> AbstractArray | AbstractScalar:
    """Preserve scalar-versus-array shape when converting TT offsets to TDB."""

    return _offset_output(seconds)
