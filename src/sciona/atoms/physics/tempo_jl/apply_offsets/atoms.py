from __future__ import annotations
"""Auto-generated atom wrappers following the sciona pattern."""


import numpy as np

import icontract
from sciona.ghost.registry import register_atom
from .witnesses import witness__zero_offset, witness_apply_offsets, witness_show

from juliacall import Main as jl


# Witness functions should be imported from the generated witnesses module

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

@register_atom(witness__zero_offset)
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

@register_atom(witness_apply_offsets)
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


from juliacall import Main as jl


def _show_ffi(io, s):
    """Wrapper that calls the Julia version of show. Passes arguments through and returns the result."""
    return jl.eval("show(io, s)")

def _zero_offset_ffi(seconds):
    """Wrapper that calls the Julia version of zero offset. Passes arguments through and returns the result."""
    return jl.eval("_zero_offset(seconds)")

def _apply_offsets_ffi(sec, ts1, ts2):
    """Wrapper that calls the Julia version of apply offsets. Passes arguments through and returns the result."""
    return jl.eval("apply_offsets(sec, ts1, ts2)")