from __future__ import annotations
"""Auto-generated atom wrappers following the sciona pattern."""


import numpy as np

import icontract
from sciona.ghost.decorators import symbolic_atom
from sciona.ghost.registry import register_atom
from .expressions import (
    APPLY_OFFSETS_DIM_MAP,
    APPLY_OFFSETS_EXPR,
    APPLY_OFFSETS_VARIABLES,
    TEMPO_BIBLIOGRAPHY,
    ZERO_OFFSET_CONSTANTS,
    ZERO_OFFSET_DIM_MAP,
    ZERO_OFFSET_EXPR,
    ZERO_OFFSET_VARIABLES,
)
from .witnesses import witness__zero_offset, witness_apply_offsets, witness_show

# Witness functions should be imported from the generated witnesses module

SYMBOLIC_REVIEW_BLOCKERS = {
    "show": (
        "No sound @symbolic_atom expression was added: this atom formats an "
        "already computed string-like time-scale object for display. It does "
        "not introduce an independent physical equation or dimensional "
        "relationship beyond identity string conversion."
    ),
}


@register_atom(witness_show)
@icontract.require(lambda io: io is not None, "io cannot be None")
@icontract.require(lambda s: s is not None, "s cannot be None")
@icontract.ensure(lambda result: result is not None, "Show output must not be None")
def show(io: str, s: str) -> str:
    """Show.

    Args:
        io (str): Description.
        s (str): Description.

    Returns:
        str: Description.
    """
    return str(s)

@symbolic_atom(
    witness__zero_offset,
    expr=ZERO_OFFSET_EXPR,
    dim_map=ZERO_OFFSET_DIM_MAP,
    constants=ZERO_OFFSET_CONSTANTS,
    variables=ZERO_OFFSET_VARIABLES,
    bibliography=TEMPO_BIBLIOGRAPHY,
)
@icontract.require(lambda seconds: seconds is not None, "seconds cannot be None")
@icontract.ensure(lambda result: result is not None, " Zero Offset output must not be None")
def _zero_offset(seconds: float) -> float:
    """Zero offset.

    Args:
        seconds (float): Description.

    Returns:
        float: Description.
    """
    return 0.0

@symbolic_atom(
    witness_apply_offsets,
    expr=APPLY_OFFSETS_EXPR,
    dim_map=APPLY_OFFSETS_DIM_MAP,
    variables=APPLY_OFFSETS_VARIABLES,
    bibliography=TEMPO_BIBLIOGRAPHY,
)
@icontract.require(lambda sec: sec is not None, "sec cannot be None")
@icontract.require(lambda ts1: ts1 is not None, "ts1 cannot be None")
@icontract.require(lambda ts2: ts2 is not None, "ts2 cannot be None")
@icontract.ensure(lambda result: result is not None, "Apply Offsets output must not be None")
def apply_offsets(sec: float, ts1: float, ts2: float) -> float:
    """Apply offsets.

    Args:
        sec (float): Description.
        ts1 (float): Description.
        ts2 (float): Description.

    Returns:
        float: Description.
    """
    return sec + ts1 - ts2


"""Auto-generated FFI bindings for julia implementations."""


def _show_ffi(io, s):
    """Wrapper that calls the Julia version of show. Passes arguments through and returns the result."""
    from juliacall import Main as jl

    return jl.eval("show(io, s)")

def _zero_offset_ffi(seconds):
    """Wrapper that calls the Julia version of zero offset. Passes arguments through and returns the result."""
    from juliacall import Main as jl

    return jl.eval("_zero_offset(seconds)")

def _apply_offsets_ffi(sec, ts1, ts2):
    """Wrapper that calls the Julia version of apply offsets. Passes arguments through and returns the result."""
    from juliacall import Main as jl

    return jl.eval("apply_offsets(sec, ts1, ts2)")
