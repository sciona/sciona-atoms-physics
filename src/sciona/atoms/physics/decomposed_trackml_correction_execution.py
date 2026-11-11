"""Explicit numeric providers for the draft tracking recipe, including corrections."""
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete prepared state and qualified numeric callables required')


@register_atom(concrete_only)
def track(prepared: object, circle_function: object, pitch_two_function: object,
          pitch_three_function: object, nearest_function: object,
          cylinder_function: object, plane_function: object,
          cylinder_intersection_function: object, plane_intersection_function: object,
          cap_correction_function: object, cylinder_correction_function: object) -> object:
    """Run configured tracking rounds with ten explicit reusable numeric providers."""
    from sciona._runtime.physics.decomposed_trackml_correction_lifecycle import execute
    return execute(**prepared, circle_function=circle_function,
                   pitch_two_function=pitch_two_function, pitch_three_function=pitch_three_function,
                   nearest_function=nearest_function, cylinder_function=cylinder_function,
                   plane_function=plane_function,
                   cylinder_intersection_function=cylinder_intersection_function,
                   plane_intersection_function=plane_intersection_function,
                   cap_correction_function=cap_correction_function,
                   cylinder_correction_function=cylinder_correction_function)
