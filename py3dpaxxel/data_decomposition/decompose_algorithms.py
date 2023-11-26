from typing import Dict, Optional, List

import numpy as np
from numpy import blackman
from scipy.fft import fft, fftfreq

from py3dpaxxel.samples.loader import Samples


class FftXYZ:
    def __init__(self):
        self.frequency_hz: Optional[List[float]] = []
        self.x: List[float] = []
        self.y: List[float] = []
        self.z: List[float] = []


class DecomposeFftAlgorithms1D:
    # https://docs.scipy.org/doc/scipy/tutorial/fft.html

    def __init__(self) -> None:
        self.algorithms: Dict[str, callable] = {
            "discrete": DecomposeFftAlgorithms1D._compute_fft_1d_discrete,
            "discrete_blackman": DecomposeFftAlgorithms1D._compute_fft_1d_discrete_blackman_window,
        }

    @staticmethod
    def _compute_fft_1d_discrete(samples: Samples) -> FftXYZ:
        n = len(samples)
        xff = fftfreq(n, samples.separation_s)[:n // 2]
        yff_x = fft(samples.x)
        yff_y = fft(samples.y)
        yff_z = fft(samples.z)

        decomposed = FftXYZ()
        decomposed.frequency_hz = xff
        decomposed.x = 2.0 / n * np.abs(yff_x[0:n // 2])
        decomposed.y = 2.0 / n * np.abs(yff_y[0:n // 2])
        decomposed.z = 2.0 / n * np.abs(yff_z[0:n // 2])

        return decomposed

    @staticmethod
    def _compute_fft_1d_discrete_blackman_window(samples: Samples) -> FftXYZ:
        n = len(samples)
        xff = fftfreq(n, samples.separation_s)[:n // 2]
        window = blackman(n)
        yff_x = fft(samples.x * window)
        yff_y = fft(samples.y * window)
        yff_z = fft(samples.z * window)

        decomposed = FftXYZ()
        decomposed.frequency_hz = xff[1:n // 2]
        decomposed.x = 2.0 / n * np.abs(yff_x[1:n // 2])
        decomposed.y = 2.0 / n * np.abs(yff_y[0:n // 2])
        decomposed.z = 2.0 / n * np.abs(yff_z[0:n // 2])

        return decomposed

    def compute(self, algo: str, samples: Samples) -> FftXYZ:
        return self.algorithms[algo](samples)
