import logging
import os.path
from typing import List, Optional

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from py3dpaxxel.data_decomposition.datavis_algorithms import DataVisFftAlgorithms1D, DataVisFftAlgorithms2D, DataVisFftAlgorithms3D
from py3dpaxxel.samples.loader import Samples, SamplesLoader
from py3dpaxxel.storage.file_filter import FileSelector


class DataVisualizerRunner:

    def __init__(self,
                 command: Optional[str],
                 input_filename: str,
                 algorithm_d1: Optional[str],
                 algorithm_d2: Optional[str],
                 algorithm_d3: Optional[str],
                 output_save: bool,
                 output_plot: bool) -> None:
        self.command: Optional[str] = command
        self.input_filename: str = input_filename
        self.algorithm_d1: Optional[str] = algorithm_d1
        self.algorithm_d2: Optional[str] = algorithm_d2
        self.algorithm_d3: Optional[str] = algorithm_d3
        self.do_save_to_file: bool = output_save
        self.do_plot: bool = output_plot

    @staticmethod
    def _fft_1d(algorithm: str, samples: Samples, window_title: Optional[str], save_filename: Optional[str]):

        fig_acc: Figure
        axes: List[Axes]
        num_fft_axes = len(DataVisFftAlgorithms1D().algorithms) if algorithm == "all" else 1
        fig_acc, axes = plt.subplots(3 + num_fft_axes, 1)
        fig_acc.suptitle("Acceleration over Time / FFT" + ("\n" + window_title) if window_title else "")
        if window_title:
            fig_acc.canvas.manager.set_window_title(window_title)
        # fig_acc.canvas.manager. full_screen_toggle()
        fig_acc.set_size_inches(60 / 2.45, 30 / 2.45)

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
            for a in DataVisFftAlgorithms1D().algorithms.keys():
                fftax = axes[fft_ax_nr]
                DataVisFftAlgorithms1D().compute(a, samples, fftax)
                fft_ax_nr += 1
        else:
            fftax = axes[3]
            DataVisFftAlgorithms1D().compute(algorithm, samples, fftax)

        if save_filename:
            fig_acc.savefig(save_filename)
        return 0

    @staticmethod
    def _fft_2d(algorithm: str, samples: Samples, _window_title: Optional[str], _save_filename: Optional[str]):
        if algorithm == "all":
            for a in DataVisFftAlgorithms2D().algorithms.keys():
                return DataVisFftAlgorithms2D().compute(a, samples)
        else:
            return DataVisFftAlgorithms2D().compute(algorithm, samples)

    @staticmethod
    def _trajectory_3d(algorithm: str, samples: Samples, _window_title: Optional[str], _save_filename: Optional[str]):
        if algorithm == "all":
            for a in DataVisFftAlgorithms2D().algorithms.keys():
                return DataVisFftAlgorithms3D().compute(a, samples)
        else:
            return DataVisFftAlgorithms3D().compute(algorithm, samples)

    def run(self) -> int:
        if not self.command:
            return -1

        if self.command == "algo":

            fs = (FileSelector(self.input_filename))
            files = fs.filter()
            logging.info(f"selected {len(files)} for plotting from {fs.directory} (filter: {fs.filename})")
            for i in range(0, len(files)):
                logging.debug(f"file {i} {files[i].full_path}")

            for i in range(0, len(files)):
                file = files[i]
                loader = SamplesLoader(file.full_path)
                samples = loader.load()

                assert (len(samples) % 2) == 0, "found odd number of samples, FFT needs even length of sample"

                logging.info(f"processing input file {i} {file.filename_ext}...")
                window_title = file.filename_no_ext
                out_filename = os.path.join(file.directory, file.filename_no_ext) if self.do_save_to_file else None
                if out_filename:
                    logging.debug(f"rendering image {file.filename_no_ext} upon user request")

                if self.algorithm_d1 is not None:
                    self._fft_1d(self.algorithm_d1, samples, window_title, out_filename)
                elif self.algorithm_d2 is not None:
                    self._fft_2d(self.algorithm_d2, samples, window_title, out_filename)
                elif self.algorithm_d3 is not None:
                    self._trajectory_3d(self.algorithm_d3, samples, window_title, out_filename)
                else:
                    logging.info("nothing to do")

            if self.do_plot:
                logging.info("plotting data...")
                plt.show()
            else:
                logging.debug("plotting skipped upon user request")

        else:
            logging.info("nothing to do")
            return -1
