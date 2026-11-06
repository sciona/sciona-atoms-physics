"""Explicit circle, pitch and projection bindings for the draft tracking recipe."""
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete prepared state and qualified geometry callables required')


@register_atom(concrete_only)
def track(prepared: object, circle_function: object, pitch_two_function: object,
          pitch_three_function: object, nearest_function: object) -> object:
    """Run configured tracking rounds with four explicit reusable geometry providers."""
    from sciona.decomposed_trackml_projection_lifecycle import execute
    return execute(**prepared, circle_function=circle_function,
                   pitch_two_function=pitch_two_function, pitch_three_function=pitch_three_function,
                   nearest_function=nearest_function)
