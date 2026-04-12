"""Auto-generated verified atom wrapper."""

import numpy as np
import icontract
from ageoa.ghost.registry import register_atom
from .witnesses import witness_dm_can_brute_force, witness_spline_bandpass_correction



@register_atom(witness_dm_can_brute_force)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def dm_can_brute_force(data: np.ndarray) -> np.ndarray:
    """Performs a brute-force shift search to maximize the signal-to-noise ratio of a folded profile.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    # Brute-force DM search: try shifts and find SNR-maximizing one
    best_snr = -np.inf
    best_profile = data.copy()
    n = len(data)
    for shift in range(n):
        rolled = np.roll(data, -shift)
        snr = np.mean(rolled) / (np.std(rolled) + 1e-15)
        if snr > best_snr:
            best_snr = snr
            best_profile = rolled
    return best_profile

@register_atom(witness_spline_bandpass_correction)
@icontract.require(lambda data: np.isfinite(data).all(), "data must contain only finite values")
@icontract.require(lambda data: data.shape[0] > 0, "data must not be empty")
@icontract.require(lambda data: data.ndim >= 1, "data must have at least one dimension")
@icontract.require(lambda data: data is not None, "data must not be None")
@icontract.require(lambda data: isinstance(data, np.ndarray), "data must be a numpy array")
@icontract.ensure(lambda result: result is not None, "result must not be None")
@icontract.ensure(lambda result: isinstance(result, np.ndarray), "result must be a numpy array")
@icontract.ensure(lambda result: result.ndim >= 1, "result must have at least one dimension")
def spline_bandpass_correction(data: np.ndarray) -> np.ndarray:
    """Subtracts instrument-induced artifacts across frequency channels using interpolative splines.

    Args:
        data: Input N-dimensional tensor or 1D scalar array.

    Returns:
        Processed output array.
    """
    # Spline bandpass correction: fit and subtract a smooth baseline
    from scipy.interpolate import UnivariateSpline
    x = np.arange(len(data), dtype=np.float64)
    spline = UnivariateSpline(x, data, s=len(data))
    return data - spline(x)
