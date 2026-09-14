"""Source-grounded TrackML runtime boundaries; no event data or maps bundled."""
from sciona.ghost.registry import register_atom


def witness_trackml_decode(payload: dict) -> dict:
    return {'kind':'TrackML.PreparedRuntime'}


@register_atom(witness_trackml_decode)
def trackml_decode(payload: dict) -> object:
    """Decode explicit versioned runtime tables, settings and layer-function grids."""
    from sciona.trackml_payload import decode_tracking_payload
    return decode_tracking_payload(payload)


def witness_trackml_track(prepared: object) -> dict:
    if prepared!={'kind':'TrackML.PreparedRuntime'}:raise ValueError('Prepared tracking runtime required')
    return {'kind':'TrackML.Assignments'}


@register_atom(witness_trackml_track)
def trackml_track(prepared: object) -> object:
    """Run source seeding, fitting, following, pairing, ranking and commitment."""
    from sciona.trackml_payload import run_decoded_tracking
    return run_decoded_tracking(prepared)


def witness_trackml_encode(assignments: object) -> dict:
    if assignments!={'kind':'TrackML.Assignments'}:raise ValueError('Tracking assignments required')
    return {'kind':'TrackML.ResultPayload'}


@register_atom(witness_trackml_encode)
def trackml_encode(assignments: object) -> dict:
    """Encode complete per-hit assignment output without file persistence."""
    from sciona.trackml_payload import encode_tracking_result
    return encode_tracking_result(assignments)
