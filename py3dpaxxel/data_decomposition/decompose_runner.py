import logging
import os.path
from typing import Optional

from py3dpaxxel.data_decomposition.decompose_algorithms import DecomposeFftAlgorithms1D, FftXYZ
from py3dpaxxel.samples.loader import Samples, SamplesLoader
from py3dpaxxel.storage.file_filter import FileSelector


class DataDecomposeRunner:

    def __init__(self,
                 command: Optional[str],
                 input_dir: str,
                 input_file_prefix: str,
                 algorithm_d1: Optional[str],
                 output_dir: str,
                 output_file_prefix: str,
                 output_overwrite: bool) -> None:
        self.command: Optional[str] = command
        self.input_dir: str = input_dir
        self.input_file_prefix: str = input_file_prefix
        self.algorithm_d1: Optional[str] = algorithm_d1
        self.output_dir: str = output_dir
        self.output_file_prefix: str = output_file_prefix
        self.output_overwrite: bool = output_overwrite

    @staticmethod
    def _fft_1d(algorithm: str, samples: Samples, save_filename: str, overwrite_existing_file: bool):
        fft_xyz: FftXYZ = DecomposeFftAlgorithms1D().compute(algorithm, samples)

        for ax in ["x", "y", "z"]:
            out_filename = f"{save_filename}-{ax}.tsv"
            if not overwrite_existing_file and os.path.isfile(out_filename):
                logging.debug(f"skipping FFT: existing file={out_filename}")
                continue
            with open(out_filename, "w") as out_file:
                logging.info(f"processing FFT file={out_filename}")
                out_file.write("freq_hz fft\n")
                for fhz, fft in zip(fft_xyz.frequency_hz, getattr(fft_xyz, ax)):
                    out_file.write(f"{fhz} {fft}\n")

    def run(self) -> int:
        if not self.command:
            return -1

        if self.command == "algo":

            fs = (FileSelector(os.path.join(self.input_dir, self.input_file_prefix) + "*"))
            files = fs.filter()
            logging.info(f"selected {len(files)} for FFT from {fs.directory} (filter: {fs.filename})")
            for i in range(0, len(files)):
                logging.debug(f"file {i} {files[i].full_path}")

            for i in range(0, len(files)):
                file = files[i]
                loader = SamplesLoader(file.full_path)
                samples = loader.load()

                assert (len(samples) % 2) == 0, "found odd number of samples, FFT needs even length of sample"
                logging.info(f"processing input file {i} {file.filename_ext}")

                out_filename = os.path.join(file.directory, self.output_file_prefix + "-" + file.filename_no_ext)

                if self.algorithm_d1 is not None:
                    self._fft_1d(self.algorithm_d1, samples, out_filename, self.output_overwrite)
                else:
                    logging.info("nothing to do")

        else:
            logging.info("nothing to do")
            return -1
