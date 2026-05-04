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
import json
import sys
import types
import uuid
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from sciona.ghost.registry import REGISTRY


PROVIDER = "sciona-atoms-physics"
EXPRESSION_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, f"sciona:{PROVIDER}:symbolic")

DEFAULT_SYMBOLIC_ATOM_MODULES = (
    "sciona.atoms.physics.astroflow.atoms",
    "sciona.atoms.physics.cosmology.atoms",
    "sciona.atoms.physics.pulsar.pipeline",
    "sciona.atoms.physics.pulsar_folding.atoms",
    "sciona.atoms.physics.pulsar_folding.dm_can",
    "sciona.atoms.particle_tracking.detector_corrections.atoms",
    "sciona.atoms.particle_tracking.helix_geometry.atoms",
    "sciona.atoms.particle_tracking.track_matching.atoms",
    "sciona.atoms.physics.skyfield.atoms",
    "sciona.atoms.physics.tempo_jl.atoms",
    "sciona.atoms.physics.tempo_jl.apply_offsets.atoms",
    "sciona.atoms.physics.tempo_jl.find_month.atoms",
    "sciona.atoms.physics.tempo_jl.find_year.atoms",
    "sciona.atoms.physics.tempo_jl.jd2cal.atoms",
    "sciona.atoms.physics.tempo_jl.offsets.atoms",
    "sciona.atoms.physics.tempo_jl.tai2utc.atoms",
    "sciona.atoms.physics.tempo_jl.tai2utc_d12.atoms",
    "sciona.atoms.physics.tempo_jl.utc2tai.atoms",
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
    source_registry = registry or _load_registry_entries_by_module(module_names)
    expressions: list[dict[str, Any]] = []
    variables: list[dict[str, Any]] = []
    validity_bounds: list[dict[str, Any]] = []

    for registry_key, entry in sorted(source_registry.items()):
        symbolic = entry.get("symbolic")
        if symbolic is None:
            continue

        atom_module = str(entry.get("module") or "")
        if atom_module not in module_names:
            continue

        atom_name = str(entry.get("name") or registry_key)
        artifact_key = _artifact_key(provider, atom_module, atom_name, entry)
        dim_signature = _compact_dim_map(entry.get("dim_signature") or symbolic.dim_map)
        symbolic_dim_signature = _compact_dim_map(symbolic.dim_map)
        expression_id = _expression_id(provider, atom_module, atom_name)
        source_expression_id = _source_expression_id(provider, atom_module, atom_name)
        expression_text = str(symbolic.to_sympy())
        canonical_expr_hash = _stable_hash("expr", symbolic.srepr_str)
        topology_hash = _stable_hash("topology", _topology_key(symbolic.srepr_str))
        dimensional_hash = _stable_hash(
            "dimensional",
            {
                "topology_hash": topology_hash,
                "dim_signature": symbolic_dim_signature,
            },
        )
        mechanism_tags = _metadata_or_heuristic_tags(
            symbolic,
            entry,
            atom_module,
            atom_name,
            "mechanism_tags",
        )
        behavioral_archetypes = _metadata_or_heuristic_tags(
            symbolic,
            entry,
            atom_module,
            atom_name,
            "behavioral_archetypes",
        )
        expression_row = {
            "artifact_key": artifact_key,
            "provider": provider,
            "atom_name": atom_name,
            "atom_module": atom_module,
            "registry_name": str(entry.get("name") or atom_name),
            "expression_id": expression_id,
            "source_expression_id": source_expression_id,
            "expression_srepr": symbolic.srepr_str,
            "expression_text": expression_text,
            "sympy_srepr": symbolic.srepr_str,
            "raw_formula": expression_text,
            "raw_formula_format": "plain_text",
            "expression_kind": "equation",
            "expression_role": "primary",
            "canonical_expr_hash": canonical_expr_hash,
            "topology_hash": topology_hash,
            "dimensional_hash": dimensional_hash,
            "parse_status": "normalized",
            "parse_confidence": 1.0,
            "review_status": "automated_pass",
            "validation_status": "passed",
            "mechanism_tags": mechanism_tags,
            "behavioral_archetypes": behavioral_archetypes,
            "variables": dict(sorted(symbolic.variables.items())),
            "dim_signature": dim_signature,
            "symbolic_dim_signature": symbolic_dim_signature,
            "constants": dict(sorted(symbolic.constants.items())),
            "bibliography": list(symbolic.bibliography),
            "local_artifact_key": _local_artifact_key(provider, atom_module, atom_name),
            "artifact_uuid": _registry_uuid(entry),
        }
        expressions.append(expression_row)

        for ordinal, (symbol, role) in enumerate(sorted(symbolic.variables.items())):
            dim_signature = symbolic_dim_signature.get(symbol, "")
            variables.append(
                {
                    "artifact_key": artifact_key,
                    "local_artifact_key": expression_row["local_artifact_key"],
                    "provider": provider,
                    "atom_name": atom_name,
                    "atom_module": atom_module,
                    "registry_name": expression_row["registry_name"],
                    "expression_id": expression_id,
                    "symbol": symbol,
                    "symbol_name": symbol,
                    "source_symbol": symbol,
                    "source_variable_id": _source_variable_id(
                        provider,
                        atom_module,
                        atom_name,
                        symbol,
                    ),
                    "role": role,
                    "variable_role": role,
                    "dim_signature": dim_signature,
                    "dimension_source": "source" if dim_signature else "unknown",
                    "assumptions_json": {
                        "dim_signature": dim_signature,
                        "symbolic_role": role,
                    },
                    "evidence_json": {
                        "source_symbol": symbol,
                        "source_expression_id": source_expression_id,
                    },
                    "ordinal": ordinal,
                }
            )

        for ordinal, (symbol, bounds) in enumerate(
            sorted(symbolic.validity_bounds.items())
        ):
            min_value, max_value = bounds
            dim_signature = symbolic_dim_signature.get(symbol, "")
            source_bound_id = _source_bound_id(
                provider,
                atom_module,
                atom_name,
                symbol,
            )
            validity_bounds.append(
                {
                    "artifact_key": artifact_key,
                    "local_artifact_key": expression_row["local_artifact_key"],
                    "provider": provider,
                    "atom_name": atom_name,
                    "atom_module": atom_module,
                    "registry_name": expression_row["registry_name"],
                    "expression_id": expression_id,
                    "symbol": symbol,
                    "variable_name": symbol,
                    "source_symbol": symbol,
                    "source_bound_id": source_bound_id,
                    "scope": "variable",
                    "bound_kind": "domain",
                    "min_value": min_value,
                    "max_value": max_value,
                    "lower_value": min_value,
                    "upper_value": max_value,
                    "lower_inclusive": True,
                    "upper_inclusive": True,
                    "dim_signature": dim_signature,
                    "validity_statement": _validity_statement(
                        symbol,
                        min_value,
                        max_value,
                    ),
                    "evidence_ref_key": source_bound_id,
                    "confidence": "high",
                    "review_status": "automated_pass",
                    "metadata": {
                        "provider": provider,
                        "atom_module": atom_module,
                        "source_expression_id": source_expression_id,
                        "source_symbol": symbol,
                        "ordinal": ordinal,
                    },
                    "ordinal": ordinal,
                }
            )

    return {
        "provider": provider,
        "modules": list(module_names),
        "artifact_symbolic_expressions": expressions,
        "artifact_symbolic_variables": variables,
        "artifact_validity_bounds": validity_bounds,
    }


def _load_registry_entries_by_module(
    module_names: tuple[str, ...],
) -> dict[str, Mapping[str, Any]]:
    """Import modules and snapshot their symbolic registry rows before collisions.

    Several generated Tempo.jl subpackages reuse atom names such as
    ``cal2jd`` and ``utc2tai``.  The global registry is keyed by atom name, so
    imports from a later module can replace entries from an earlier one.  The
    publication manifest is module-scoped, so capture rows immediately after
    each import/reload under a module-qualified key.
    """

    entries: dict[str, Mapping[str, Any]] = {}
    for module_name in module_names:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
        for atom_name, entry in REGISTRY.items():
            symbolic = entry.get("symbolic")
            if symbolic is None:
                continue
            if str(entry.get("module") or "") != module_name:
                continue
            entries[f"{module_name}:{atom_name}"] = entry
    return entries


def to_matcher_symbolic_expression_rows(
    expression_rows: Iterable[Mapping[str, Any]],
    *,
    artifact_id_by_key: Mapping[str, str],
    version_id_by_key: Mapping[str, str],
) -> list[dict[str, Any]]:
    """Return matcher staging rows without writing database records.

    The manifest cannot know database-generated artifact/version ids.  This
    adapter keeps publication loading explicit by requiring the caller to map
    each ``artifact_key`` to the artifact and version ids resolved by the
    loader.
    """

    rows: list[dict[str, Any]] = []
    for row in expression_rows:
        artifact_key = str(row["artifact_key"])
        rows.append(
            {
                "expression_id": row["expression_id"],
                "artifact_id": artifact_id_by_key[artifact_key],
                "version_id": version_id_by_key[artifact_key],
                "expression_kind": row["expression_kind"],
                "expression_role": row["expression_role"],
                "sympy_srepr": row["sympy_srepr"],
                "canonical_expr_hash": row["canonical_expr_hash"],
                "topology_hash": row["topology_hash"],
                "dimensional_hash": row["dimensional_hash"],
                "raw_formula": row["raw_formula"],
                "raw_formula_format": row["raw_formula_format"],
                "source_expression_id": row["source_expression_id"],
                "parse_status": row["parse_status"],
                "parse_confidence": row["parse_confidence"],
                "review_status": row["review_status"],
                "validation_status": row["validation_status"],
                "mechanism_tags": list(row["mechanism_tags"]),
                "behavioral_archetypes": list(row["behavioral_archetypes"]),
                "assumptions_json": {
                    "provider": row["provider"],
                    "atom_name": row["atom_name"],
                    "atom_module": row["atom_module"],
                    "variables": row["variables"],
                    "constants": row["constants"],
                    "dim_signature": row["dim_signature"],
                    "symbolic_dim_signature": row["symbolic_dim_signature"],
                },
                "evidence_json": {
                    "artifact_key": artifact_key,
                    "local_artifact_key": row["local_artifact_key"],
                    "registry_name": row["registry_name"],
                    "artifact_uuid": row["artifact_uuid"],
                    "bibliography": row["bibliography"],
                },
            }
        )
    return rows


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


def _expression_id(provider: str, atom_module: str, atom_name: str) -> str:
    return str(
        uuid.uuid5(
            EXPRESSION_NAMESPACE,
            _source_expression_id(provider, atom_module, atom_name),
        )
    )


def _source_expression_id(provider: str, atom_module: str, atom_name: str) -> str:
    return f"{provider}:{atom_module}:{atom_name}"


def _source_variable_id(
    provider: str,
    atom_module: str,
    atom_name: str,
    symbol: str,
) -> str:
    return f"{_source_expression_id(provider, atom_module, atom_name)}:variable:{symbol}"


def _source_bound_id(
    provider: str,
    atom_module: str,
    atom_name: str,
    symbol: str,
) -> str:
    return f"{_source_expression_id(provider, atom_module, atom_name)}:bound:{symbol}"


def _validity_statement(symbol: str, lower: Any, upper: Any) -> str:
    if lower is None and upper is None:
        return ""
    if lower is None:
        return f"{symbol} <= {upper}"
    if upper is None:
        return f"{symbol} >= {lower}"
    return f"{lower} <= {symbol} <= {upper}"


def _stable_hash(kind: str, payload: Any) -> str:
    encoded = json.dumps(
        {"kind": kind, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _topology_key(srepr_str: str) -> str:
    try:
        import sympy as sp

        from sciona.ghost.symbolic import deserialize_expr, serialize_expr

        expr = deserialize_expr(srepr_str)
        symbols = sorted(expr.free_symbols, key=lambda symbol: str(symbol))
        replacements = {
            symbol: sp.Symbol(f"_v{i}", real=symbol.is_real)
            for i, symbol in enumerate(symbols)
        }
        return serialize_expr(expr.xreplace(replacements))
    except Exception:  # noqa: BLE001 - fallback keeps manifest generation robust.
        return srepr_str


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


def _metadata_or_heuristic_tags(
    symbolic: Any,
    entry: Mapping[str, Any],
    atom_module: str,
    atom_name: str,
    field_name: str,
) -> list[str]:
    explicit = _coerce_string_list(getattr(symbolic, field_name, None))
    if not explicit:
        explicit = _coerce_string_list(entry.get(field_name))
    if explicit:
        return explicit
    return _heuristic_tags(atom_module, atom_name, field_name)


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_values = [value]
    elif isinstance(value, Iterable):
        raw_values = [str(item) for item in value]
    else:
        return []
    return _dedupe_sorted(
        item.strip().lower().replace(" ", "_")
        for item in raw_values
        if item and str(item).strip()
    )


def _heuristic_tags(atom_module: str, atom_name: str, field_name: str) -> list[str]:
    module = atom_module.lower()
    name = atom_name.lower()
    tags: list[str] = []
    if "pulsar_folding" in module:
        if name == "dm_can_brute_force":
            tags.extend(
                ["pulsar_search", "shift_search", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["argmax_selection", "snr_scoring"]
            )
        elif name == "spline_bandpass_correction":
            tags.extend(
                ["bandpass_correction", "instrumental_baseline", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["baseline_subtraction", "spline_smoothing"]
            )
        else:
            tags.extend(
                ["dispersion", "pulsar_search", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["candidate_scoring", "delay_model"]
            )
    if "pulsar.pipeline" in module:
        if name == "delay_from_dm":
            tags.extend(
                ["dispersion_measure", "pulsar_timing", "signal_propagation"]
                if field_name == "mechanism_tags"
                else ["delay_model", "inverse_square_scaling"]
            )
        elif name == "de_disperse":
            tags.extend(
                ["dedispersion", "pulsar_search", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["delay_alignment", "time_series_shift"]
            )
        elif name == "fold_signal":
            tags.extend(
                ["periodic_signal", "pulsar_search", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["phase_folding", "windowed_average"]
            )
        elif name == "snr":
            tags.extend(
                ["noise_model", "signal_detection", "signal_processing"]
                if field_name == "mechanism_tags"
                else ["log_ratio", "peak_to_background"]
            )
    if "astroflow" in module:
        tags.extend(
            ["dedispersion", "pulsar_search", "signal_processing"]
            if field_name == "mechanism_tags"
            else ["channel_aggregation", "delay_alignment"]
        )
    if "cosmology" in module:
        tags.extend(
            ["cosmological_redshift", "flux_correction", "photometry"]
            if field_name == "mechanism_tags"
            else ["multiplicative_scaling", "redshift_correction"]
        )
    if "helix_geometry" in module:
        tags.extend(
            ["geometric_reconstruction", "helix_geometry", "particle_tracking"]
            if field_name == "mechanism_tags"
            else ["geometric_fit", "track_reconstruction"]
        )
        if "nearest_point" in name:
            tags.append("distance_minimization")
        if "least_squares" in name:
            tags.append("least_squares_fit")
    if "detector_corrections" in module:
        if name == "coordinate_rescaling_for_knn":
            tags.extend(
                ["detector_geometry", "knn_search", "particle_tracking"]
                if field_name == "mechanism_tags"
                else ["coordinate_rescaling", "radius_normalization"]
            )
        elif name == "perturbative_cap_correction":
            tags.extend(
                ["detector_geometry", "particle_tracking", "surface_correction"]
                if field_name == "mechanism_tags"
                else ["azimuthal_radial_correction", "perturbative_update"]
            )
        elif name == "perturbative_cylinder_correction":
            tags.extend(
                ["detector_geometry", "particle_tracking", "surface_correction"]
                if field_name == "mechanism_tags"
                else ["curvature_scaled_update", "perturbative_update"]
            )
    if "track_matching" in module:
        if "cylinder_intersection" in name:
            tags.extend(
                ["helix_geometry", "particle_tracking", "surface_intersection"]
                if field_name == "mechanism_tags"
                else ["cylinder_intersection", "phase_advance"]
            )
        elif "cap_intersection" in name:
            tags.extend(
                ["helix_geometry", "particle_tracking", "surface_intersection"]
                if field_name == "mechanism_tags"
                else ["cap_intersection", "phase_advance"]
            )
        elif name == "bayesian_neighbor_evaluation":
            tags.extend(
                ["bayesian_filtering", "particle_tracking", "track_extension"]
                if field_name == "mechanism_tags"
                else ["likelihood_ratio_cut", "normalized_distance"]
            )
        elif name == "greedy_track_commit":
            tags.extend(
                ["deduplication", "particle_tracking", "track_commitment"]
                if field_name == "mechanism_tags"
                else ["greedy_selection", "loss_fraction_gate"]
            )
    if "skyfield" in module:
        tags.extend(
            ["astrometry", "coordinate_transform", "vector_geometry"]
            if field_name == "mechanism_tags"
            else ["angular_geometry", "coordinate_transform"]
        )
    if "tempo_jl" in module:
        if "tai2utc_d12" in module:
            tags.extend(
                ["leap_second", "tai_utc_conversion", "time_scale_conversion"]
                if field_name == "mechanism_tags"
                else ["inverse_time_mapping", "leap_offset"]
            )
        elif module.endswith("tempo_jl.atoms"):
            if name == "graph_time_scale_management":
                tags.extend(
                    ["time_scale_conversion", "time_scale_graph"]
                    if field_name == "mechanism_tags"
                    else ["identity_mapping", "path_transform"]
                )
            elif name == "high_precision_duration":
                tags.extend(
                    ["precision_management", "time_scale_conversion"]
                    if field_name == "mechanism_tags"
                    else ["fractional_decomposition", "time_duration_split"]
                )
        elif (
            "tempo_jl.find_year" in module
            or "tempo_jl.find_month" in module
            or "tempo_jl.jd2cal" in module
            or "tempo_jl.tai2utc" in module
            or "tempo_jl.utc2tai" in module
        ):
            if name in {"utc2tai", "tai2utc"}:
                tags.extend(
                    ["leap_second", "tai_utc_conversion", "time_scale_conversion"]
                    if field_name == "mechanism_tags"
                    else ["inverse_time_mapping", "leap_offset"]
                )
            elif name in {"hms2fd", "fd2hms", "fd2hmsf"}:
                tags.extend(
                    ["calendar_time", "time_of_day_conversion"]
                    if field_name == "mechanism_tags"
                    else ["fractional_day_conversion", "unit_conversion"]
                )
            elif name in {"cal2jd", "calhms2jd", "jd2cal", "jd2calhms"}:
                tags.extend(
                    ["calendar_conversion", "julian_date", "time_scale_conversion"]
                    if field_name == "mechanism_tags"
                    else ["calendar_coordinate_mapping", "epoch_offset"]
                )
            elif name in {
                "time_from_secondinday",
                "time_from_secondinday_fraction",
            }:
                tags.extend(
                    ["calendar_time", "time_of_day_conversion"]
                    if field_name == "mechanism_tags"
                    else ["seconds_decomposition", "unit_conversion"]
                )
            elif name == "datetime_from_seconds":
                tags.extend(
                    ["calendar_conversion", "julian_date", "time_scale_conversion"]
                    if field_name == "mechanism_tags"
                    else ["calendar_coordinate_mapping", "epoch_offset"]
                )
            else:
                tags.extend(
                    ["calendar_arithmetic", "julian_date"]
                    if field_name == "mechanism_tags"
                    else ["calendar_lookup", "integer_time_mapping"]
                )
        else:
            tags.extend(
                ["relativistic_timing", "time_scale_conversion"]
                if field_name == "mechanism_tags"
                else ["periodic_correction", "time_offset"]
            )
    return _dedupe_sorted(tags)


def _dedupe_sorted(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})


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
    if needs_tempo and "juliacall" not in sys.modules:
        juliacall_module = types.ModuleType("juliacall")
        juliacall_module.__spec__ = importlib.machinery.ModuleSpec("juliacall", None)

        class _JuliaMainStub:
            def eval(self, expression: str) -> Any:
                raise ImportError(
                    "juliacall is required to execute this Tempo atom: "
                    f"{expression}"
                )

        juliacall_module.Main = _JuliaMainStub()
        sys.modules["juliacall"] = juliacall_module

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
