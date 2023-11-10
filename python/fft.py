#!/bin/env python3

import argparse
import csv
import logging
import os
import sys
from enum import Enum
from typing import Dict, List

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy import blackman
from numpy.fft import fftfreq, fft

from lib.device_constants import OutputDataRateDelay, OutputDataRate


class LogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Samples:
    def __init__(self, output_data_rate: OutputDataRate):
        self.separation_ms = OutputDataRateDelay[output_data_rate] * 1000
        self.run = []
        self.index = []
        self.timestamp_ms = []
        self.x = []
        self.y = []
        self.z = []

    def __len__(self):
        return len(self.index)


class FftAlgorithms:

    def __init__(self):
        self.algorithms: Dict[str, callable] = {
            "1d": FftAlgorithms._compute_fft_1d_discrete,
            "1dbw": FftAlgorithms._compute_fft_1d_discrete_blackman_window,
        }

    @staticmethod
    def _compute_fft_1d_discrete(samples: Samples, axs: List[Axes]):
        n = len(samples)
        xff = fftfreq(n, samples.separation_ms / 1000.0)[:n // 2]
        yff_x = fft(samples.x)
        yff_y = fft(samples.y)
        yff_z = fft(samples.z)

        axs[0].plot(xff, 2.0 / n * np.abs(yff_x[0:n // 2]))
        axs[0].plot(xff, 2.0 / n * np.abs(yff_y[0:n // 2]))
        axs[0].plot(xff, 2.0 / n * np.abs(yff_z[0:n // 2]))

        axs[0].set(ylabel="amp [mg]", xlabel="f [Hz]")
        axs[0].legend(["x", "y", "z"])
        axs[0].set_title("1D Discrete", loc="left")
        return

    @staticmethod
    def _compute_fft_1d_discrete_blackman_window(samples: Samples, axs: List[Axes]):
        n = len(samples)
        xff = fftfreq(n, samples.separation_ms / 1000.0)[:n // 2]
        window = blackman(n)

        ywf_x = (samples.x * window)
        yff_x = fft(samples.x)
        ywf_y = (samples.y * window)
        yff_y = fft(samples.y)
        ywf_z = (samples.z * window)
        yff_z = fft(samples.z)

        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(yff_x[1:n // 2]), '-r')
        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(ywf_x[1:n // 2]), '--r')

        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(yff_y[1:n // 2]), '-g')
        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(ywf_y[1:n // 2]), '--g')

        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(yff_z[1:n // 2]), '-b')
        axs[0].semilogy(xff[1:n // 2], 2.0 / n * np.abs(ywf_z[1:n // 2]), '--b')

        axs[0].legend(['x FFT', 'x FFT + W.', 'y FFT', 'y FFT + W.', 'z FFT', 'z FFT + W.'])
        axs[0].set_title("1D Discrete w. Blackman W.", loc="left")
        return

    def compute(self, algo: str, samples: Samples, axs: List[Axes]):
        return self.algorithms[algo](samples, axs)


class Args:
    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        def is_file(file_path: str) -> str | None:
            return file_path if os.path.isfile(file_path) else None

        self.parser.add_argument(
            "-f", "--file",
            help="Specify input file (*.tsv)",
            type=is_file,
            default="example.tsv")

        # TODO https://docs.scipy.org/doc/scipy/tutorial/fft.html
        self.parser.add_argument(
            "-a", "--algorithm",
            help="FFT algorithm",
            choices=["all"].extend(FftAlgorithms().algorithms.keys()),
            default="all")

        self.parser.add_argument(
            "-p", "--plot",
            help="Visualizes data",
            action="store_true")

        self.parser.add_argument(
            "-l", "--log",
            help="Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            choices=[e.name for e in LogLevel],
            default="INFO")

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner:

    def __init__(self) -> None:
        self._cli_args: Args = Args()
        logging.basicConfig(level=LogLevel[self.args.log].value)

    @property
    def args(self):
        return self._cli_args.args

    @property
    def parser(self):
        return self._cli_args.parser

    @staticmethod
    def read_samples(file_name: str):
        samples = Samples(OutputDataRate.ODR3200)

        with open(file_name, "r") as f:
            reader = csv.DictReader(f, delimiter=" ")
            row: Dict[str, int | float]
            for row in reader:
                samples.run.append(int(row["run"]))
                index = int(row["sample"])
                samples.index.append(index)
                samples.timestamp_ms.append(index * samples.separation_ms)
                samples.x.append(float(row["x"]))
                samples.y.append(float(row["y"]))
                samples.z.append(float(row["z"]))

        return samples

    def run(self) -> int:
        samples = self.read_samples(self.args.file)
        fig_acc: Figure
        axes: List[Axes]
        num_fft_axes = len(FftAlgorithms().algorithms) if self.args.algorithm == "all" else 1
        fig_acc, axes = plt.subplots(3 + num_fft_axes, 1)
        fig_acc.suptitle('Acceleration over Time / FFT')

        axes[0].plot(samples.timestamp_ms, samples.x, color='r', linestyle="solid", marker=None, label="x")
        axes[1].plot(samples.timestamp_ms, samples.y, color='g', linestyle="solid", marker=None, label="y")
        axes[2].plot(samples.timestamp_ms, samples.z, color='b', linestyle="solid", marker=None, label="z")

        for ax in axes[:-1]:
            ax.grid()
            ax.legend()
            ax.set(ylabel="acc [mg]", xlabel="time [ms]")

        if self.args.algorithm == "all":
            ax_nr = 3
            for a in FftAlgorithms().algorithms.keys():
                FftAlgorithms().compute(a, samples, [axes[ax_nr]])
                ax_nr += 1
        else:
            FftAlgorithms().compute(self.args.algorithm, samples, [axes[3]])

        plt.show()
        return 0


if __name__ == "__main__":
    sys.exit(Runner().run())
