from __future__ import annotations
from sciona.ghost.abstract import AbstractArray, AbstractScalar, AbstractDistribution, AbstractSignal


def witness_dedisperse(
    data: AbstractSignal,
    DM: float,
    fchan: float,
    width: float,
    tsamp: float,
) -> AbstractSignal:
    """Corrects for dispersion — the frequency-dependent delay that radio pulses acquire while traveling through interstellar plasma. Higher frequencies arrive first; this witness models the removal of that delay using the Dispersion Measure (DM, the integrated electron density along the line of sight) while preserving the 2D time-frequency spectrogram structure. Returns abstract output metadata without performing real computation."""
    data.assert_domain("time")
    return AbstractSignal(
        shape=data.shape,
        dtype="float64",
        sampling_rate=data.sampling_rate,
        domain="time",
        units="power",
    )


def witness_fold_signal(data: AbstractSignal, period: int) -> AbstractSignal:
    """Folds a 2D time-frequency spectrogram at the pulsar's rotation period to produce a 1D pulse profile. Folding sums the signal at the same rotational phase across many periods, boosting the periodic pulsar signal while averaging down random noise. Returns abstract output metadata without performing real computation."""
    data.assert_domain("time")
    if len(data.shape) < 2:
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
    """Computes the Signal-to-Noise Ratio (SNR) of a folded pulsar profile — the ratio of peak pulse amplitude to the background noise level. Higher SNR indicates a more confidently detected pulsar. Returns abstract output metadata without performing real computation."""
    return AbstractScalar(dtype="float64", min_val=0.0)


def witness_delay_from_dm(DM: float, freq_emitted: float) -> AbstractScalar:
    """Calculates the time delay caused by interstellar dispersion at a given frequency. The delay depends on the Dispersion Measure (DM — integrated electron density along the line of sight, in pc/cm^3) and the observing frequency; lower frequencies are delayed more. Returns abstract output metadata without performing real computation."""
    return AbstractScalar(dtype="float64", min_val=0.0)
