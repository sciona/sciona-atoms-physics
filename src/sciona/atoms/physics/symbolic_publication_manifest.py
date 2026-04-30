"""Build publication-shaped symbolic manifests for physics atoms.

The manifest is intentionally side-effect-free: it imports selected atom
modules so their decorators populate the in-process REGISTRY, then converts
the symbolic registry entries into plain dictionaries.  It does not require
database identifiers and does not write publication artifacts.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.machinery
import importlib.util
import sys
import types
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from sciona.ghost.registry import REGISTRY


PROVIDER = "sciona-atoms-physics"

DEFAULT_SYMBOLIC_ATOM_MODULES = (
    "sciona.atoms.physics.pulsar_folding.dm_can",
    "sciona.atoms.particle_tracking.helix_geometry.atoms",
    "sciona.atoms.physics.skyfield.atoms",
    "sciona.atoms.physics.tempo_jl.apply_offsets.atoms",
    "sciona.atoms.physics.tempo_jl.offsets.atoms",
)


def build_symbolic_publication_manifest(
    modules: Iterable[str] = DEFAULT_SYMBOLIC_ATOM_MODULES,
    *,
    provider: str = PROVIDER,
    registry: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return publication scaffold rows for selected symbolic atoms.

    The returned dictionary is shaped for later insertion into
    ``artifact_symbolic_expressions``, ``artifact_symbolic_variables``, and
    ``artifact_validity_bounds``.  ``artifact_key`` is either a registry UUID
    when one is present, or a deterministic local key derived from provider,
    module, and atom name.
    """

    module_names = tuple(modules)
    _install_optional_import_shims(module_names)
    for module_name in module_names:
        importlib.import_module(module_name)

    source_registry = registry or REGISTRY
    expressions: list[dict[str, Any]] = []
    variables: list[dict[str, Any]] = []
    validity_bounds: list[dict[str, Any]] = []

    for atom_name, entry in sorted(source_registry.items()):
        symbolic = entry.get("symbolic")
        if symbolic is None:
            continue

        atom_module = str(entry.get("module") or "")
        if atom_module not in module_names:
            continue

        artifact_key = _artifact_key(provider, atom_module, atom_name, entry)
        dim_signature = _compact_dim_map(entry.get("dim_signature") or symbolic.dim_map)
        symbolic_dim_signature = _compact_dim_map(symbolic.dim_map)
        expression_row = {
            "artifact_key": artifact_key,
            "provider": provider,
            "atom_name": atom_name,
            "atom_module": atom_module,
            "registry_name": str(entry.get("name") or atom_name),
            "expression_srepr": symbolic.srepr_str,
            "expression_text": str(symbolic.to_sympy()),
            "variables": dict(sorted(symbolic.variables.items())),
            "dim_signature": dim_signature,
            "symbolic_dim_signature": symbolic_dim_signature,
            "constants": dict(sorted(symbolic.constants.items())),
            "bibliography": list(symbolic.bibliography),
            "local_artifact_key": _local_artifact_key(provider, atom_module, atom_name),
            "artifact_uuid": _registry_uuid(entry),
        }
        expressions.append(expression_row)

        for symbol, role in sorted(symbolic.variables.items()):
            variables.append(
                {
                    "artifact_key": artifact_key,
                    "provider": provider,
                    "atom_name": atom_name,
                    "symbol": symbol,
                    "role": role,
                    "dim_signature": symbolic_dim_signature.get(symbol, ""),
                }
            )

        for symbol, bounds in sorted(symbolic.validity_bounds.items()):
            min_value, max_value = bounds
            validity_bounds.append(
                {
                    "artifact_key": artifact_key,
                    "provider": provider,
                    "atom_name": atom_name,
                    "symbol": symbol,
                    "min_value": min_value,
                    "max_value": max_value,
                }
            )

    return {
        "provider": provider,
        "modules": list(module_names),
        "artifact_symbolic_expressions": expressions,
        "artifact_symbolic_variables": variables,
        "artifact_validity_bounds": validity_bounds,
    }


def _registry_uuid(entry: Mapping[str, Any]) -> str | None:
    for key in ("artifact_uuid", "uuid", "id"):
        value = entry.get(key)
        if value:
            return str(value)
    return None


def _artifact_key(
    provider: str,
    atom_module: str,
    atom_name: str,
    entry: Mapping[str, Any],
) -> str:
    registry_uuid = _registry_uuid(entry)
    if registry_uuid is not None:
        return registry_uuid
    return _local_artifact_key(provider, atom_module, atom_name)


def _local_artifact_key(provider: str, atom_module: str, atom_name: str) -> str:
    digest = hashlib.sha256(
        f"{provider}:{atom_module}:{atom_name}".encode("utf-8")
    ).hexdigest()[:16]
    return f"local:{provider}:{atom_module}:{atom_name}:{digest}"


def _compact_dim_map(dim_map: Mapping[str, Any]) -> dict[str, str]:
    compact: dict[str, str] = {}
    for symbol, dim_signature in sorted(dim_map.items()):
        if hasattr(dim_signature, "to_compact"):
            compact[str(symbol)] = str(dim_signature.to_compact())
        elif dim_signature is None:
            compact[str(symbol)] = ""
        else:
            compact[str(symbol)] = str(dim_signature)
    return compact


def _install_optional_import_shims(module_names: tuple[str, ...]) -> None:
    """Provide minimal runtime-only shims needed to import symbolic atoms."""

    needs_tempo = any(
        module_name.startswith("sciona.atoms.physics.tempo_jl")
        for module_name in module_names
    )
    if needs_tempo and "sciona.atoms.physics.tempo_jl" not in sys.modules:
        package_name = "sciona.atoms.physics.tempo_jl"
        tempo_module = types.ModuleType(package_name)
        tempo_module.__path__ = [str(Path(__file__).with_name("tempo_jl"))]
        tempo_module.__package__ = package_name
        tempo_module.__spec__ = importlib.machinery.ModuleSpec(
            package_name,
            None,
            is_package=True,
        )
        sys.modules[package_name] = tempo_module

    needs_skyfield = any(
        module_name.startswith("sciona.atoms.physics.skyfield")
        for module_name in module_names
    )
    if needs_skyfield and not _module_available("skyfield"):
        skyfield_module = types.ModuleType("skyfield")
        functions_module = types.ModuleType("skyfield.functions")
        skyfield_module.__spec__ = importlib.machinery.ModuleSpec("skyfield", None)
        functions_module.__spec__ = importlib.machinery.ModuleSpec(
            "skyfield.functions",
            None,
        )

        def _not_available(*_args: Any, **_kwargs: Any) -> Any:
            raise ImportError("skyfield is required to execute this atom")

        functions_module.angle_between = _not_available
        functions_module._to_spherical_and_rates = _not_available
        skyfield_module.functions = functions_module
        sys.modules.setdefault("skyfield", skyfield_module)
        sys.modules.setdefault("skyfield.functions", functions_module)


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ValueError:
        return module_name in sys.modules
