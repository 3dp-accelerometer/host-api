#!/bin/env python3

import argparse
import logging
import operator
import os
import sys
from enum import Enum
from typing import Dict, List

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy import blackman
from scipy.fft import fft, ifft, fftfreq

from lib.samples_loader import Samples, SamplesLoader


class LogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class FftAlgorithms1D:
    # https://docs.scipy.org/doc/scipy/tutorial/fft.html

    def __init__(self):
        self.algorithms: Dict[str, callable] = {
            "discrete": FftAlgorithms1D._compute_fft_1d_discrete,
            "discrete_blackman": FftAlgorithms1D._compute_fft_1d_discrete_blackman_window,
        }

    @staticmethod
    def plot_ifft(samples: Samples, xax: Axes, yax: Axes, zax: Axes):
        ixff = ifft(fft(samples.x))
        iyff = ifft(fft(samples.y))
        izff = ifft(fft(samples.z))

        xax.plot(samples.timestamp_ms, ixff, color="orange", alpha=0.2, linestyle="--", marker=".", label="ifft(x)")
        yax.plot(samples.timestamp_ms, iyff, color="orange", alpha=0.2, linestyle="--", marker=".", label="ifft(y)")
        zax.plot(samples.timestamp_ms, izff, color="orange", alpha=0.2, linestyle="--", marker=".", label="ifft(z)")

    @staticmethod
    def _compute_fft_1d_discrete(samples: Samples, fftax: Axes) -> int:
        n = len(samples)
        xff = fftfreq(n, samples.separation_ms / 1000.0)[:n // 2]
        yff_x = fft(samples.x)
        yff_y = fft(samples.y)
        yff_z = fft(samples.z)

        fftax.plot(xff, 2.0 / n * np.abs(yff_x[0:n // 2]), color="r", linestyle="solid", marker=None, label="fft(x)")
        fftax.plot(xff, 2.0 / n * np.abs(yff_y[0:n // 2]), color="g", linestyle="solid", marker=None, label="fft(y)")
        fftax.plot(xff, 2.0 / n * np.abs(yff_z[0:n // 2]), color="b", linestyle="solid", marker=None, label="fft(z)")
        fftax.set_title("1D Discrete", loc="left")
        fftax.set(ylabel="amplitude", xlabel="f [Hz]")
        fftax.legend(loc="upper right")

        return 0

    @staticmethod
    def _compute_fft_1d_discrete_blackman_window(samples: Samples, fftax: Axes) -> int:
        # fft
        n = len(samples)
        xff = fftfreq(n, samples.separation_ms / 1000.0)[:n // 2]

        yff_x = fft(samples.x)
        yff_y = fft(samples.y)
        yff_z = fft(samples.z)

        window = blackman(n)
        ywf_x = fft(samples.x * window)
        ywf_y = fft(samples.y * window)
        ywf_z = fft(samples.z * window)

        # fft
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(yff_x[1:n // 2]), "-r", label="fft(x)")
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(ywf_x[1:n // 2]), "--r", label="fft_BW(x)")
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(yff_y[1:n // 2]), "-g", label="fft(y)")
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(ywf_y[1:n // 2]), "--g", label="fft_BW(y)")
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(yff_z[1:n // 2]), "-b", label="fft(z)")
        fftax.plot(xff[1:n // 2], 2.0 / n * np.abs(ywf_z[1:n // 2]), "--b", label="fft_BW(z)")
        fftax.set_title("1D Discrete + 1D Discrete w. Blackman Window (BW)", loc="left")
        fftax.set(ylabel="amplitude", xlabel="f [Hz]")
        fftax.legend(loc="upper right")

        return 0

    def compute(self, algo: str, samples: Samples, fftax: Axes):
        return self.algorithms[algo](samples, fftax)


class FftAlgorithms2D:

    def __init__(self):
        self.algorithms: Dict[str, callable] = {
            "discrete": FftAlgorithms2D._compute_fft_2d_discrete,
        }

    @staticmethod
    def _compute_fft_2d_discrete(samples: Samples) -> int:
        logging.error("not implemented yet")
        return -1

    def compute(self, algo: str, samples: Samples) -> int:
        return self.algorithms[algo](samples)


class FftAlgorithms3D:

    def __init__(self):
        self.algorithms: Dict[str, callable] = {
            "trajectory": FftAlgorithms3D._compute_trajectory_from_acceleration_stream,
        }

    @staticmethod
    def _compute_trajectory_from_acceleration_stream(samples: Samples) -> int:
        # https://web.archive.org/web/20090701062452/http://www.ugrad.math.ubc.ca/coursedoc/math101/notes/applications/velocity.html

        separation_ms = samples.separation_ms
        # sensor replies in mg, where 1000mg = 1g = 9.81m/s^2 = 9810 mm/s^2 = 9.81mm/ms^2

        accs_xyz_mg = [acc for acc in zip(samples.x, samples.y, samples.z)]
        # test data
        # accs_xyz_mg = [(1000, 0, 0), (1000, 0, 0), (-1000, 1000, 0), (-1000, 1000, 0), (0, -1000, 1000), (0, -1000, 1000), (0, 0, -1000), (0, 0, -1000)]
        v_xyz_mm_ms = (0, 0, 0)
        positions_mm = [(0, 0, 0)]

        def compute_x1_mm(x0_mm: float, v_mm_ms: float, acc_mg: float):
            # todo:                                       vvv this factor shall not be here, why is it required?
            return x0_mm + (v_mm_ms * separation_ms * separation_ms) + 0.5 * 9.81 * (acc_mg / 1000.0) * separation_ms * separation_ms

        # todo calibration:
        #  - implement offset calibration
        #  - implement gain calibration
        #  - implement orientation calibration (needed for trajectory; assume orientation never changes)

        #  orientation_calibration = (0, 0, 0)
        #  orientation_calibration = (0, 0, 1000)
        #  orientation_calibration = (+0000.000, +00000, +0902.800)
        orientation_calibration = (+0007.800, +0007.800, +0897.000)

        for acc_xyz_mg in accs_xyz_mg:
            print(f"ac {acc_xyz_mg[0]:+.9f} {acc_xyz_mg[1]:+.9f} {acc_xyz_mg[2]:+.9f}")
            p0 = positions_mm[-1]
            print(f"p0 {p0[0]:+.9f} {p0[1]:+.9f} {p0[2]:+.9f}")
            p1 = (compute_x1_mm(p0[0], v_xyz_mm_ms[0], acc_xyz_mg[0] - orientation_calibration[0]),
                  compute_x1_mm(p0[1], v_xyz_mm_ms[1], acc_xyz_mg[1] - orientation_calibration[1]),
                  compute_x1_mm(p0[2], v_xyz_mm_ms[2], acc_xyz_mg[2] - orientation_calibration[2]))
            print(f"p1 {p1[0]:+.9f} {p1[1]:+.9f} {p1[2]:+.9f}")
            v_xyz_mm_separation_ms = tuple(map(operator.sub, p1, p0))
            v_xyz_mm_ms = v_xyz_mm_separation_ms  # tuple(map(operator.mul, v_xyz_mm_separation_ms, (1 / separation_ms, 1 / separation_ms, 1 / separation_ms)))
            print(f"v  {v_xyz_mm_separation_ms[0]:+.9f} {v_xyz_mm_separation_ms[1]:+.9f} {v_xyz_mm_separation_ms[2]:+.9f}")
            print(f"v  {v_xyz_mm_ms[0]:+.9f} {v_xyz_mm_ms[1]:+.9f} {v_xyz_mm_ms[2]:+.9f}")
            positions_mm.append(p1)

        ax = plt.figure().add_subplot(projection='3d')
        x, y, z = list(zip(*positions_mm))
        ax.plot(x, y, z, marker='o', markevery=[0], label="trajectory")
        ax.plot([0, 100], [0, 0], [0, 0], marker='o', markevery=[0], label="x")
        ax.plot([0, 0], [0, 100], [0, 0], marker='o', markevery=[0], label="y")
        ax.plot([0, 0], [0, 0], [0, 100], marker='o', markevery=[0], label="z")
        ax.legend()
        ax.set(ylabel="y [mm]", xlabel="x [mm]", zlabel="z [mm]")

        plt.show()

        return 0

    def compute(self, algo: str, samples: Samples):
        return self.algorithms[algo](samples)


class Args:
    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(
            dest='command',
            title="command (required)",
            description="Run command with the loaded configuration.")

        sup = sub_parsers.add_parser(
            "algo",
            help="FFT algorithm (1-D, 2-D N-D)",
            description="FFT Algorithm applied to input data.")
        grp = sup.add_mutually_exclusive_group()

        grp.add_argument(
            "-1", "--d1",
            help="Performs FFT 1D algorithms: discrete 1D, discrete 1D with Blackman window or both.",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms1D().algorithms.keys()],
            const=[k for k in FftAlgorithms1D().algorithms.keys()][0])

        grp.add_argument(
            "-2", "--d2",
            help="FFT 2D algorithms: no algorithm implemented yet (TODO)",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms2D().algorithms.keys()],
            const=[k for k in FftAlgorithms2D().algorithms.keys()][0])

        grp.add_argument(
            "-3", "--d3",
            help="FFT 3D algorithms: compute trajectory from acceleration. Requires offset, gain and orientation calibration.",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms3D().algorithms.keys()],
            const=[k for k in FftAlgorithms3D().algorithms.keys()][0])

        sub_group = self.parser.add_argument_group(
            "Flags",
            description="General flags applied to all commands.")

        def is_file(file_path: str) -> str | None:
            return file_path if os.path.isfile(file_path) else None

        sub_group.add_argument(
            "-f", "--file",
            help="Specify input file (*.tsv)",
            type=is_file,
            default="example.tsv")

        sub_group.add_argument(
            "-p", "--plot",
            help="Visualizes data",
            action="store_true")

        sub_group.add_argument(
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
    def fft_1d(algorithm: str, samples: Samples):

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

        # signal re-construction to verify loss: ifft(fft())
        FftAlgorithms1D.plot_ifft(samples, xax, yax, zax)

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
    def fft_2d(algorithm: str, samples: Samples):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms2D().compute(a, samples)
        else:
            return FftAlgorithms2D().compute(algorithm, samples)

    @staticmethod
    def trajectory_3d(algorithm: str, samples: Samples):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms3D().compute(a, samples)
        else:
            return FftAlgorithms3D().compute(algorithm, samples)

    def run(self) -> int:
        loader = SamplesLoader(self.args.file)
        samples = loader.load()
        assert (len(samples) % 2) == 0, "found odd samples length, FFT needs even length of sample"

        if self.args.command == "algo":
            if self.args.d1 is not None:
                return self.fft_1d(self.args.d1, samples)
            elif self.args.d2 is not None:
                return self.fft_2d(self.args.d2, samples)
            elif self.args.d3 is not None:
                return self.trajectory_3d(self.args.d3, samples)
            else:
                logging.info("nothing to do")
        else:
            logging.info("nothing to do")
            return -1


if __name__ == "__main__":
    sys.exit(Runner().run())
