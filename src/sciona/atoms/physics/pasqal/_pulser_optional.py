from __future__ import annotations

import logging
import os
from collections import Counter
from dataclasses import replace
from typing import Hashable, Mapping, Sequence

import networkx as nx
import numpy as np


class MissingQuantumOptionalDependency(ImportError):
    """Raised when the Pulser quantum optional dependency stack is absent."""


def _require_quantum_stack() -> dict[str, object]:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    try:
        import pulser as pl
        from emu_sv import BitStrings, SVBackend, SVConfig, StateResult
        from pulser import Pulse, Register
        from pulser.channels.dmm import DMM
        from pulser.devices import AnalogDevice, DigitalAnalogDevice
        from pulser.waveforms import ConstantWaveform, InterpolatedWaveform
    except ImportError as exc:
        raise MissingQuantumOptionalDependency(
            "Install the Pulser quantum extra with `pip install sciona-atoms-physics[quantum]` "
            "to run the Pasqal molecular-docking quantum MWIS solver."
        ) from exc

    return {
        "AnalogDevice": AnalogDevice,
        "BitStrings": BitStrings,
        "ConstantWaveform": ConstantWaveform,
        "DMM": DMM,
        "DigitalAnalogDevice": DigitalAnalogDevice,
        "InterpolatedWaveform": InterpolatedWaveform,
        "Pulse": Pulse,
        "Register": Register,
        "SVBackend": SVBackend,
        "SVConfig": SVConfig,
        "StateResult": StateResult,
        "pl": pl,
    }


def _coordinates_for_graph(
    graph: nx.Graph,
    coordinates_layout: Mapping[Hashable, Sequence[float] | np.ndarray],
) -> dict[Hashable, tuple[float, float]]:
    coords: dict[Hashable, tuple[float, float]] = {}
    for node in graph.nodes:
        if node not in coordinates_layout:
            continue
        coord = np.asarray(coordinates_layout[node], dtype=float)
        if coord.shape[0] < 2:
            raise ValueError("each coordinate must have at least two entries")
        coords[node] = (float(coord[0]), float(coord[1]))
    if not coords:
        raise ValueError("coordinates_layout must contain coordinates for graph nodes")
    return coords


def _compute_interaction_bounds(
    register_coord: Mapping[Hashable, Sequence[float] | np.ndarray],
    graph: nx.Graph,
) -> tuple[float, float]:
    stack = _require_quantum_stack()
    digital_analog = stack["DigitalAnalogDevice"]
    interaction_coefficient = float(digital_analog.interaction_coeff)  # type: ignore[attr-defined]
    edge_distances: list[float] = []
    non_edge_distances: list[float] = []
    nodes = list(register_coord)
    for idx, left in enumerate(nodes):
        left_coord = np.asarray(register_coord[left], dtype=float)
        for right in nodes[idx + 1 :]:
            distance = float(np.linalg.norm(left_coord - np.asarray(register_coord[right], dtype=float)))
            if distance <= 0.0:
                continue
            if graph.has_edge(left, right):
                edge_distances.append(distance)
            else:
                non_edge_distances.append(distance)
    if not edge_distances:
        raise ValueError("graph must contain at least one edge for quantum interaction bounds")
    u_min = interaction_coefficient / (max(edge_distances) ** 6)
    u_max = interaction_coefficient / (min(non_edge_distances) ** 6) if non_edge_distances else u_min
    return float(u_min), float(u_max)


def _build_adiabatic_sequence(register: object, parameters: Mapping[str, object]) -> object:
    stack = _require_quantum_stack()
    analog_device = stack["AnalogDevice"]
    dmm_cls = stack["DMM"]
    digital_analog_device = stack["DigitalAnalogDevice"]
    duration = int(parameters.get("duration", 4000))
    dmm = dmm_cls(
        clock_period=4,
        min_duration=16,
        max_duration=2**26,
        mod_bandwidth=8,
        bottom_detuning=-2 * np.pi * 20,
        total_bottom_detuning=-2 * np.pi * 2000,
    )
    mock_device = replace(
        digital_analog_device.to_virtual(),
        dmm_objects=(dmm, dmm_cls()),
        reusable_channels=True,
    )

    channel_name = "rydberg_global"
    dmm_channel_name = "dmm_0"
    raw_dmm_map = parameters.get("dmm_map", {})
    dmm_map = {
        qubit_id: float(raw_dmm_map.get(qubit_id, 0.0))  # type: ignore[union-attr]
        for qubit_id in list(getattr(register, "qubit_ids"))
    }
    detuning_map = register.define_detuning_map(dmm_map, dmm_channel_name)  # type: ignore[attr-defined]
    omega_list = [1e-9, 4.850055051963065, 12.566370614359172, 11.882582923954192, 1e-9]
    delta_list = [
        -analog_device.channels[channel_name].max_abs_detuning,  # type: ignore[attr-defined]
        -23.735663070454464,
        2.429518510655143,
        13.330733571729787,
        31.06390344878028,
    ]

    sequence = stack["pl"].Sequence(register, mock_device)  # type: ignore[attr-defined]
    sequence.declare_channel(channel_name, channel_name)
    sequence.config_detuning_map(detuning_map, dmm_channel_name)
    sequence.add(
        stack["Pulse"](
            stack["InterpolatedWaveform"](duration, omega_list),  # type: ignore[operator]
            stack["InterpolatedWaveform"](duration, delta_list),  # type: ignore[operator]
            0,
        ),  # type: ignore[operator]
        channel_name,
    )
    sequence.add_dmm_detuning(
        stack["ConstantWaveform"](duration, float(parameters.get("dmm_detuning", 0.0))),  # type: ignore[operator]
        dmm_channel_name,
    )
    return sequence


def _sample_sv(sequence: object, n_samples: int, dt: int) -> dict[str, int]:
    stack = _require_quantum_stack()
    duration = int(sequence.get_duration())  # type: ignore[attr-defined]
    safe_dt = max(1, min(int(dt), max(1, duration // 2)))
    sequence_duration = duration // safe_dt * safe_dt
    eval_times = [time / sequence_duration for time in range(safe_dt, sequence_duration, safe_dt)] or [1.0]
    final_time = eval_times[-1]
    bitstrings = stack["BitStrings"](evaluation_times=[final_time], num_shots=n_samples)  # type: ignore[operator]
    state = stack["StateResult"](evaluation_times=[final_time])  # type: ignore[operator]
    config = stack["SVConfig"](
        dt=safe_dt,
        observables=[bitstrings, state],
        log_level=logging.WARN,
    )  # type: ignore[operator]
    results = stack["SVBackend"](sequence, config=config).run()  # type: ignore[operator]
    counts: Counter[str] = results.state[-1].sample(num_shots=n_samples)
    return {str(bitstring): int(count) for bitstring, count in counts.items()}


def solve_quantum_mwis(
    graph: nx.Graph,
    lattice_id_coord_dic: Mapping[Hashable, Sequence[float] | np.ndarray],
    mis_sample_quantity: int,
    *,
    n_samples: int = 128,
    dt: int = 1000,
) -> list[set[int]]:
    """Run the source-style Pulser adiabatic solver and decode top bitstrings."""
    stack = _require_quantum_stack()
    register_coord = _coordinates_for_graph(graph, lattice_id_coord_dic)
    register = stack["Register"](register_coord)  # type: ignore[operator]
    qubit_ids = list(getattr(register, "qubit_ids"))
    weights_by_node = nx.get_node_attributes(graph, "weight")
    weights = np.asarray([float(weights_by_node.get(node, 1.0)) for node in qubit_ids])
    max_weight = float(np.max(weights)) if weights.size else 1.0
    if max_weight <= 0.0:
        max_weight = 1.0
    normalised_weights = weights / max_weight
    min_weight = float(np.min(normalised_weights)) if normalised_weights.size else 1.0
    weights_rev = 1.0 - normalised_weights
    _, u_max = _compute_interaction_bounds(register_coord, graph)
    parameters: dict[str, object] = {
        "amplitude_maximum": u_max,
        "detuning_maximum": 2.0 * u_max,
        "dmm_detuning": -31.06390344878028 * (1.0 - min_weight),
        "dmm_map": dict(zip(qubit_ids, [float(value) for value in weights_rev])),
        "duration": 4000,
    }
    sequence = _build_adiabatic_sequence(register, parameters)
    counts = _sample_sv(sequence, n_samples=n_samples, dt=dt)
    solutions: list[set[int]] = []
    for bitstring in sorted(counts, key=lambda key: counts[key], reverse=True):
        solution = {int(qubit_ids[idx]) for idx, bit in enumerate(bitstring) if int(bit) == 1}
        solutions.append(solution)
        if len(solutions) >= mis_sample_quantity:
            break
    return solutions
