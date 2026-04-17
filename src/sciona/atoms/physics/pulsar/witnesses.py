from __future__ import annotations

from sciona.ghost.abstract import AbstractScalar, AbstractSignal


def witness_dedisperse(
    data: AbstractSignal,
    DM: float,
    fchan: float,
    width: float,
    tsamp: float,
) -> AbstractSignal:
    """Return abstract metadata for a 2D time-frequency dedispersion step."""
    data.assert_domain("time")
    if len(data.shape) != 2:
        raise ValueError("Dedisperse requires 2D input (Time, Frequency)")

    return AbstractSignal(
        shape=data.shape,
        dtype="float64",
        sampling_rate=data.sampling_rate,
        domain="time",
        units="power",
    )


def witness_fold_signal(data: AbstractSignal, period: int) -> AbstractSignal:
    """Return abstract metadata for folding a 2D spectrogram into a 1D profile."""
    data.assert_domain("time")
    if len(data.shape) != 2:
        raise ValueError("Fold signal requires 2D input (Time, Frequency)")
    if period <= 0:
        raise ValueError("period must be positive")

    return AbstractSignal(
        shape=(period,),
        dtype="float64",
        sampling_rate=data.sampling_rate,
        domain="time",
        units="normalized_power",
    )


def witness_snr(arr: AbstractSignal) -> AbstractScalar:
    """Return abstract metadata for the folded-profile SNR scalar."""
    if len(arr.shape) != 1:
        raise ValueError("SNR requires 1D input")
    if arr.shape[0] <= 0:
        raise ValueError("Input array must not be empty")

    return AbstractScalar(dtype="float64", min_val=0.0)


def witness_delay_from_dm(DM: float, freq_emitted: float) -> AbstractScalar:
    """Return abstract metadata for a non-negative dispersion delay scalar."""
    return AbstractScalar(dtype="float64", min_val=0.0)
