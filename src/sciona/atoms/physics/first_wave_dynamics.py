"""Corrected first-wave Newtonian dynamics; explicit runtime position expression."""
from sciona.ghost.registry import register_atom


def witness_first_wave_dynamics(payload: dict) -> dict:
    return {'kind': 'FirstWave.SymbolicAndSampledDynamics'}


@register_atom(witness_first_wave_dynamics)
def first_wave_dynamics(payload: dict) -> dict:
    """Differentiate position twice, compute constant-mass force and solve acceleration."""
    from sciona.physics_ingest.first_wave_dynamics_execution import execute_dynamics
    return execute_dynamics(payload)
