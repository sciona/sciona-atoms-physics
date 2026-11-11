"""Explicit geometry bindings for the complete tracking lifecycle; draft provider."""
from sciona.ghost.registry import register_atom


def concrete_only(*args,**kwargs):
    raise ValueError('Concrete prepared state and qualified geometry callables required')


@register_atom(concrete_only)
def track(prepared: object,circle_function: object,pitch_two_function: object,pitch_three_function: object) -> object:
    """Run all configured tracking rounds using explicit reusable geometry operations."""
    from sciona._runtime.physics.decomposed_trackml_lifecycle import execute
    return execute(**prepared,circle_function=circle_function,
                   pitch_two_function=pitch_two_function,pitch_three_function=pitch_three_function)
