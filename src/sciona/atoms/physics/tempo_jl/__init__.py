"""tempo_jl physics atoms.

Keep the package root import-light while still configuring the writable Julia
runtime used elsewhere in the stack. Concrete Julia-backed modules remain
importable from their subpackages.
"""

from __future__ import annotations

__all__: list[str] = []
