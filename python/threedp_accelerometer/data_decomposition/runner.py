import logging
from typing import List

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from threedp_accelerometer.data_decomposition.datavis_algorithms import FftAlgorithms1D, FftAlgorithms2D, FftAlgorithms3D
from threedp_accelerometer.samples.loader import Samples, SamplesLoader


class DataVisualizerRunner:

    def __init__(self,
                 command: str | None,
                 input_file_name: str,
                 algorithm_d1: str | None,
                 algorithm_d2: str | None,
                 algorithm_d3: str | None):
        self.command: str | None = command
        self.input_file_name: str = input_file_name
        self.algorithm_d1: str | None = algorithm_d1
        self.algorithm_d2: str | None = algorithm_d2
        self.algorithm_d3: str | None = algorithm_d3

    @staticmethod
    def _fft_1d(algorithm: str, samples: Samples):

        fig_acc: Figure
        axes: List[Axes]
        num_fft_axes = len(FftAlgorithms1D().algorithms) if algorithm == "all" else 1
        fig_acc, axes = plt.subplots(3 + num_fft_axes, 1)
        fig_acc.suptitle("Acceleration over Time / FFT")

        xax, yax, zax = axes[:3]
        xax.plot(samples.timestamp_ms, samples.x, color="r", linestyle="solid", marker=None, label="x")
        yax.plot(samples.timestamp_ms, samples.y, color="g", linestyle="solid", marker=None, label="y")
        zax.plot(samples.timestamp_ms, samples.z, color="b", linestyle="solid", marker=None, label="z")

        for ax in xax, yax, zax:
            ax.grid()
            ax.set(ylabel="acc [mg]", xlabel="time [ms]")
            ax.legend(loc="upper right")
            ax.set_ylim([-2000, 2000])

        # signal re-construction to verify loss: ifft(fft())
        # FftAlgorithms1D.plot_ifft(samples, xax, yax, zax)

        # fft
        if algorithm == "all":
            fft_ax_nr = 3
            for a in FftAlgorithms1D().algorithms.keys():
                fftax = axes[fft_ax_nr]
                FftAlgorithms1D().compute(a, samples, fftax)
                fft_ax_nr += 1
        else:
            fftax = axes[3]
            FftAlgorithms1D().compute(algorithm, samples, fftax)

        plt.show()
        return 0

    @staticmethod
    def _fft_2d(algorithm: str, samples: Samples):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms2D().compute(a, samples)
        else:
            return FftAlgorithms2D().compute(algorithm, samples)

    @staticmethod
    def _trajectory_3d(algorithm: str, samples: Samples):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms3D().compute(a, samples)
        else:
            return FftAlgorithms3D().compute(algorithm, samples)

    def run(self) -> int:
        if not self.command:
            return -1

        loader = SamplesLoader(self.input_file_name)
        samples = loader.load()
        assert (len(samples) % 2) == 0, "found odd samples length, FFT needs even length of sample"

        if self.command == "algo":
            if self.algorithm_d1 is not None:
                return self._fft_1d(self.algorithm_d1, samples)
            elif self.algorithm_d2 is not None:
                return self._fft_2d(self.algorithm_d2, samples)
            elif self.algorithm_d3 is not None:
                return self._trajectory_3d(self.algorithm_d3, samples)
            else:
                logging.info("nothing to do")
        else:
            logging.info("nothing to do")
            return -1
