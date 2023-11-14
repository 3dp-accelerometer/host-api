import logging
import os.path
from typing import List, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from threedp_accelerometer.cli.file_filter import FileSelector
from threedp_accelerometer.data_decomposition.datavis_algorithms import FftAlgorithms1D, FftAlgorithms2D, FftAlgorithms3D
from threedp_accelerometer.samples.loader import Samples, SamplesLoader


class DataVisualizerRunner:

    def __init__(self,
                 command: Union[str, None],
                 input_filename: str,
                 algorithm_d1: Union[str, None],
                 algorithm_d2: Union[str, None],
                 algorithm_d3: Union[str, None],
                 output_save: bool,
                 output_plot: bool) -> None:
        self.command: Union[str, None] = command
        self.input_filename: str = input_filename
        self.algorithm_d1: Union[str, None] = algorithm_d1
        self.algorithm_d2: Union[str, None] = algorithm_d2
        self.algorithm_d3: Union[str, None] = algorithm_d3
        self.do_save_to_file: bool = output_save
        self.do_plot: bool = output_plot

    @staticmethod
    def _fft_1d(algorithm: str, samples: Samples, window_title: Union[str, None], do_plot: bool, save_filename: Union[str, None]):

        fig_acc: Figure
        axes: List[Axes]
        num_fft_axes = len(FftAlgorithms1D().algorithms) if algorithm == "all" else 1
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
            for a in FftAlgorithms1D().algorithms.keys():
                fftax = axes[fft_ax_nr]
                FftAlgorithms1D().compute(a, samples, fftax)
                fft_ax_nr += 1
        else:
            fftax = axes[3]
            FftAlgorithms1D().compute(algorithm, samples, fftax)

        if save_filename:
            fig_acc.savefig(save_filename)
        # return plt.show()
        return 0

    @staticmethod
    def _fft_2d(algorithm: str, samples: Samples, _window_title: Union[str, None], _do_plot: bool, _save_filename: Union[str, None]):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms2D().compute(a, samples)
        else:
            return FftAlgorithms2D().compute(algorithm, samples)

    @staticmethod
    def _trajectory_3d(algorithm: str, samples: Samples, _window_title: Union[str, None], _do_plot: bool, _save_filename: Union[str, None]):
        if algorithm == "all":
            for a in FftAlgorithms2D().algorithms.keys():
                return FftAlgorithms3D().compute(a, samples)
        else:
            return FftAlgorithms3D().compute(algorithm, samples)

    def run(self) -> int:
        if not self.command:
            return -1

        if self.command == "algo":

            fs = (FileSelector(self.input_filename))
            files = fs.filter()
            logging.info(f"selected {len(files)} for plotting from {fs.directory} (filter: {fs.filename})")
            for i in range(0, len(files)):
                logging.info(f"file {i} {files[i].full_path}")

            for i in range(0, len(files)):
                file = files[i]
                loader = SamplesLoader(file.full_path)
                samples = loader.load()

                assert (len(samples) % 2) == 0, "found odd number of samples, FFT needs even length of sample"

                logging.debug(f"processing file {i} {file.filename_ext}...")
                window_title = file.filename_no_ext
                out_filename = os.path.join(file.directory, file.filename_no_ext) if self.do_save_to_file else None
                if out_filename:
                    logging.debug(f"rendering image {file.filename_no_ext} upon user request")

                if self.algorithm_d1 is not None:
                    self._fft_1d(self.algorithm_d1, samples, window_title, self.do_plot, out_filename)
                elif self.algorithm_d2 is not None:
                    self._fft_2d(self.algorithm_d2, samples, window_title, self.do_plot, out_filename)
                elif self.algorithm_d3 is not None:
                    self._trajectory_3d(self.algorithm_d3, samples, window_title, self.do_plot, out_filename)
                else:
                    logging.info("nothing to do")
                logging.info(f"processing file {file.filename_ext}... done")

            if self.do_plot:
                logging.info(f"plotting data...")
                plt.show()
                logging.info(f"plotting data... done")
            else:
                logging.debug("plotting skipped upon user request")

        else:
            logging.info("nothing to do")
            return -1
