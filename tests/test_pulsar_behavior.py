from __future__ import annotations

import math

import numpy as np
import pytest

from sciona.atoms.physics.pulsar.pipeline import SNR, de_disperse, delay_from_DM, fold_signal


def test_delay_from_dm_matches_wrapper_formula() -> None:
    delay = delay_from_DM(2.41, 100.0)
    assert delay == pytest.approx(1.0)


def test_de_disperse_applies_integer_channel_shift() -> None:
    data = np.arange(8.0).reshape(4, 2)

    result = de_disperse(data, DM=2.41, fchan=100.0, width=100.0, tsamp=1.0)

    expected = np.array(
        [
            [0.0, 1.0],
            [0.0, 3.0],
            [2.0, 5.0],
            [4.0, 7.0],
        ]
    )
    assert np.array_equal(result, expected)


def test_fold_signal_averages_complete_periods() -> None:
    data = np.arange(12.0).reshape(6, 2)

    result = fold_signal(data, period=3)

    assert np.array_equal(result, np.array([3.5, 5.5, 7.5]))


def test_snr_matches_log_peak_to_absolute_mean_ratio() -> None:
    snr = SNR(np.array([0.0, 1.0, 0.0]))
    assert snr == pytest.approx(math.log(3.0))
