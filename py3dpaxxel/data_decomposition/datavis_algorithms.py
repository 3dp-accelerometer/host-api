import logging
import operator
from typing import Dict

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from numpy import blackman
from scipy.fft import fft, ifft, fftfreq

from py3dpaxxel.samples.loader import Samples


class DataVisFftAlgorithms1D:
    # https://docs.scipy.org/doc/scipy/tutorial/fft.html

    def __init__(self) -> None:
        self.algorithms: Dict[str, callable] = {
            "discrete": DataVisFftAlgorithms1D._compute_fft_1d_discrete,
            "discrete_blackman": DataVisFftAlgorithms1D._compute_fft_1d_discrete_blackman_window,
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
        xff = fftfreq(n, samples.separation_s)[:n // 2]
        yff_x = fft(samples.x)
        yff_y = fft(samples.y)
        yff_z = fft(samples.z)

        fftax.plot(xff, 2.0 / n * np.abs(yff_x[0:n // 2]), color="r", linestyle="solid", marker=None, label="fft(x)")
        fftax.plot(xff, 2.0 / n * np.abs(yff_y[0:n // 2]), color="g", linestyle="solid", marker=None, label="fft(y)")
        fftax.plot(xff, 2.0 / n * np.abs(yff_z[0:n // 2]), color="b", linestyle="solid", marker=None, label="fft(z)")
        fftax.set_title("1D Discrete", loc="left")
        fftax.set(ylabel="amplitude", xlabel="f [Hz]")
        fftax.legend(loc="upper right")
        fftax.set_ylim([0, 100])

        return 0

    @staticmethod
    def _compute_fft_1d_discrete_blackman_window(samples: Samples, fftax: Axes) -> int:
        # fft
        n = len(samples)
        xff = fftfreq(n, samples.separation_s)[:n // 2]

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


class DataVisFftAlgorithms2D:

    def __init__(self) -> None:
        self.algorithms: Dict[str, callable] = {
            "discrete": DataVisFftAlgorithms2D._compute_fft_2d_discrete,
        }

    @staticmethod
    def _compute_fft_2d_discrete(_samples: Samples) -> int:
        logging.error("not implemented yet")
        return -1

    def compute(self, algo: str, samples: Samples) -> int:
        return self.algorithms[algo](samples)


class DataVisFftAlgorithms3D:

    def __init__(self) -> None:
        self.algorithms: Dict[str, callable] = {
            "trajectory": DataVisFftAlgorithms3D._compute_trajectory_from_acceleration_stream,
        }

    @staticmethod
    def _compute_trajectory_from_acceleration_stream(samples: Samples) -> int:
        # https://web.archive.org/web/20090701062452/http://www.ugrad.math.ubc.ca/coursedoc/math101/notes/applications/velocity.html

        separation_ms = samples.separation_s * 1000
        # sensor replies in mg, where 1000mg = 1g = 9.81m/s^2 = 9810 mm/s^2 = 9.81mm/ms^2

        accs_xyz_mg = [acc for acc in zip(samples.x, samples.y, samples.z)]
        # test data
        # accs_xyz_mg = [(1000, 0, 0), (1000, 0, 0), (-1000, 1000, 0), (-1000, 1000, 0), (0, -1000, 1000), (0, -1000, 1000), (0, 0, -1000), (0, 0, -1000)]
        v_xyz_mm_ms = (0, 0, 0)
        positions_mm = [(0, 0, 0)]

        def compute_x1_mm(x0_mm: float, v_mm_ms: float, acc_mg: float):
            # todo:                                       vvv this factor shall not be here, why is it required?
            return x0_mm + (v_mm_ms * separation_ms / 10) + 0.5 * 9.81 * (acc_mg / 1000.0) * separation_ms * separation_ms

        # todo calibration:
        #  - implement offset calibration
        #  - implement gain calibration
        #  - implement orientation calibration (needed for trajectory; assume orientation never changes)

        #  orientation_calibration = (0, 0, 0)
        #  orientation_calibration = (0, 0, 1000)
        #  orientation_calibration = (+0000.000, +00000, +0902.800)
        # orientation_calibration = (+0007.800, +0007.800, +0897.000)
        orientation_calibration = (-1014.000, +0000.000, -0093.600)

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

        # plt.show()

        return 0

    def compute(self, algo: str, samples: Samples):
        return self.algorithms[algo](samples)
