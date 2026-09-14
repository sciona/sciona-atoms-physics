"""Original analytical tracking, with explicit array ports and bounded options."""
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom
from .loader import load_source_modules


def witness_find_tracks(detector_modules: AbstractArray, observations: AbstractArray,
                       extension_steps: int = 11, commitment_rounds: int = 1,
                       commitment_limit: int = 1000) -> AbstractArray:
    if len(detector_modules.shape) != 2 or detector_modules.shape[1] != 6:
        raise ValueError('Detector module matrix must have six columns')
    if len(observations.shape) != 2 or observations.shape[1] != 6:
        raise ValueError('Observation matrix must have six columns')
    return AbstractArray(shape=(observations.shape[0],), dtype='int64')


def _matrix(value, label):
    raw = np.asarray(value)
    if raw.dtype.kind not in 'iuf' or raw.ndim != 2 or raw.shape[1] != 6 or not len(raw):
        raise ValueError(label+' must be a nonempty real matrix with six columns')
    matrix = raw.astype(np.float64, copy=True)
    if not np.isfinite(matrix).all():
        raise ValueError(label+' must be finite')
    return matrix


@register_atom(witness_find_tracks)
def find_tracks(detector_modules: NDArray[np.float64], observations: NDArray[np.float64],
                extension_steps: int = 11, commitment_rounds: int = 1,
                commitment_limit: int = 1000) -> NDArray[np.int64]:
    """Return original-source track labels aligned with observation input rows.

    Detector rows: volume_id, layer_id, cx, cy, cz, module_hv. Observation rows:
    volume_id, layer_id, module_id, x, y, z. These are the original public source
    API fields; units must match. Observation coordinates round to float32 to
    preserve original library loading semantics, then source arithmetic uses
    float64. Identity is generated from row order. Label zero means unassigned.

    Requires source-compatible concentric finite cylinders and planar caps:
    exactly seven cap radial clusters with three gaps, monotone cylinder
    coverage, and occupied layers adequate for four-neighbor queries. The source
    validates geometry; configurations it cannot process fail explicitly.
    Finite integral volume/layer/module identifiers and positive module half
    lengths required. No cell features, learned calibration, scoring, tuning,
    or nonphysical postprocessing. No real-event accuracy guarantee.

    Runs complete source seeding, iterative extension, fitting, ranking, pairing,
    pruning and commitment. Source defaults otherwise apply, except ranking is
    kept nonzero for small events and redundant-track pruning begins at the
    first extension iteration. Each invocation has fresh source state and
    does not mutate inputs, use files for observations, or patch global imports.
    """
    modules = _matrix(detector_modules, 'Detector modules')
    hits = _matrix(observations, 'Observations')
    for values in (modules[:, :2], hits[:, :3]):
        if np.any(values != np.floor(values)) or np.any(values < 0) or np.any(values > 32767):
            raise ValueError('Identifiers must be nonnegative integers at most 32767')
    if np.any(modules[:, 5] <= 0):
        raise ValueError('Positive module half lengths required')
    for value, minimum, maximum in [(extension_steps, 2, 100), (commitment_rounds, 1, 100),
                                     (commitment_limit, 1, 1000000)]:
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not minimum <= value <= maximum:
            raise ValueError('Invalid bounded integer tracking option')
    with np.errstate(over='ignore', invalid='ignore'):
        coordinates = hits[:, 3:].astype(np.float32)
    if not np.isfinite(coordinates).all():
        raise ValueError('Observation coordinates must fit finite float32')
    source = load_source_modules()
    geometry_source = source['trackml_solution.geometry']
    geometry = geometry_source.GeometrySpec()
    geometry.detectors_df = pd.DataFrame(modules, columns=['volume_id', 'layer_id', 'cx', 'cy', 'cz', 'module_hv'])
    geometry.detectors_df[['volume_id', 'layer_id']] = modules[:, :2].astype(np.int32)
    detector = geometry_source.DetectorSpec(geometry)
    frame = pd.DataFrame(coordinates, columns=['x', 'y', 'z'])
    for i, key in enumerate(['volume_id', 'layer_id', 'module_id']):
        frame[key] = hits[:, i].astype(np.int32)
    frame['hit_id'] = np.arange(1, len(hits)+1, dtype=np.int64)
    data = source['trackml_solution.data']

    def memory_event(prefix, parts):
        if parts != ['hits']:
            raise ValueError('Only observation-only tracking is supported')
        return (frame.copy(deep=True),)

    data.load_event = memory_event
    captured = []

    class InMemoryAlgorithm(source['trackml_solution.algorithm'].Algorithm):
        def log(self, *args, **kwargs):
            pass

        def createOrAppendSubmissionFile(self, filename, submission_df, append=False):
            if append or captured:
                raise ValueError('Unexpected multiple event outputs')
            captured.append(submission_df.copy(deep=True))

    algorithm = InMemoryAlgorithm(detector, params={
        'follow__niter': int(extension_steps), 'commit__niter': int(commitment_rounds),
        'commit__nmax': int(commitment_limit), 'rank__ntop_qu': 1.,
        'follow__drop_start': 0})
    event = data.Event('event000001', with_truth=False, with_cells=False)
    algorithm.findTracks(None, [event], submission_filename='memory',
                         analysis=False, score_intermediate=False, score_final=False)
    if len(captured) != 1:
        raise ValueError('Tracking did not produce exactly one result')
    result = captured[0].sort_values('hit_id')
    if not np.array_equal(result.hit_id.to_numpy(), frame.hit_id.to_numpy()):
        raise ValueError('Tracking output must cover each observation exactly once')
    labels = result.track_id.to_numpy(dtype=np.int64, copy=True)
    if np.any(labels < 0):
        raise ValueError('Tracking produced negative labels')
    return labels
