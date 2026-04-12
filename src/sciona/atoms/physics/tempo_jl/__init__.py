"""tempo_jl physics atoms.

Keep the package root import-light while still configuring the writable Julia
runtime used elsewhere in the stack. Concrete Julia-backed modules remain
importable from their subpackages.
"""

from __future__ import annotations

from sciona.atoms.physics._julia_runtime import configure_juliacall_env

configure_juliacall_env()

try:
    import juliacall  # noqa: F401
except Exception:
    pass

__all__: list[str] = []
