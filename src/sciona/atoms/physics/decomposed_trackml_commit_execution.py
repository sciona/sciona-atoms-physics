"""Explicit numeric providers for the draft tracking recipe, including ordered selection."""
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete prepared state and qualified numeric callables required')


@register_atom(concrete_only)
def track(prepared: object, circle_function: object, pitch_two_function: object,
          pitch_three_function: object, nearest_function: object,
          cylinder_function: object, plane_function: object,
          cylinder_intersection_function: object, plane_intersection_function: object,
          cap_correction_function: object, cylinder_correction_function: object,
          search_fit_function: object, search_k_function: object, search_radius_function: object,
          decision_function: object, commit_function: object) -> object:
    """Run configured tracking rounds with fifteen explicit reusable numeric providers."""
    from sciona.decomposed_trackml_commit_lifecycle import execute
    return execute(**prepared, circle_function=circle_function,
                   pitch_two_function=pitch_two_function, pitch_three_function=pitch_three_function,
                   nearest_function=nearest_function, cylinder_function=cylinder_function,
                   plane_function=plane_function,
                   cylinder_intersection_function=cylinder_intersection_function,
                   plane_intersection_function=plane_intersection_function,
                   cap_correction_function=cap_correction_function,
                   cylinder_correction_function=cylinder_correction_function,
                   search_fit_function=search_fit_function, search_k_function=search_k_function,
                   search_radius_function=search_radius_function, decision_function=decision_function,
                   commit_function=commit_function)
