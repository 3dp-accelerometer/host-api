import logging
import os.path
from typing import Optional, Callable, Tuple

from py3dpaxxel.data_decomposition.decompose_algorithms import DecomposeFftAlgorithms1D, FftXYZ
from py3dpaxxel.samples.loader import Samples, SamplesLoader
from py3dpaxxel.storage.file_filter import FileSelector
from py3dpaxxel.storage.filename_meta import FilenameMeta


class DataDecomposeRunner(Callable[[], Tuple[int, int, int, int]]):

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
    def _fft_1d(algorithm: str, samples: Samples, save_filename: str, overwrite_existing_file: bool) -> Tuple[int, int, int]:
        fft_xyz: FftXYZ = DecomposeFftAlgorithms1D().compute(algorithm, samples)
        total = 0
        processed = 0
        skipped = 0

        for ax in ["x", "y", "z"]:
            total += 1
            out_filename = f"{save_filename}-{ax}.tsv"
            if not overwrite_existing_file and os.path.isfile(out_filename):
                # logging.debug(f"skipping FFT: existing file={out_filename}")
                skipped += 1
                continue
            with open(out_filename, "w") as out_file:
                # logging.info(f"processing FFT file={out_filename}")
                out_file.write("freq_hz fft\n")
                processed += 1
                for fhz, fft in zip(fft_xyz.frequency_hz, getattr(fft_xyz, ax)):
                    out_file.write(f"{fhz} {fft}\n")

        return total, processed, skipped

    def __call__(self) -> Tuple[int, int, int, int]:
        return self.run()

    def run(self) -> Tuple[int, int, int, int]:
        total = 0
        processed = 0
        skipped = 0

        if not self.command:
            return -1, total, processed, skipped

        if self.command == "algo":

            fs = (FileSelector(os.path.join(self.input_dir, self.input_file_prefix) + "*"))
            in_files = fs.filter()
            logging.info(f"selected {len(in_files)} for FFT from {fs.directory} (filter: {fs.filename})")
            # for i in range(0, len(in_files)):
            #     logging.debug(f"file {i} {in_files[i].full_path}")

            for i in range(0, len(in_files)):
                in_file = in_files[i]
                loader = SamplesLoader(in_file.full_path)
                samples = loader.load()
                total += 1

                if not samples.has_meta():
                    skipped += 1
                    continue

                if samples.is_empty():
                    skipped += 1
                    logging.warning(f"skip empty stream: file nr={i} file={in_file.filename_ext}")
                    continue

                assert (len(samples) % 2) == 0, "found odd number of samples, FFT needs even length of sample"
                # logging.info(f"processing input file {i} {in_file.filename_ext}")

                file_meta = FilenameMeta().from_filename(in_file.filename_ext)
                out_filename = os.path.join(self.output_dir, f"{self.output_file_prefix}-{file_meta.prefix_2}-"
                                                             f"{file_meta.year:04}{file_meta.month:02}{file_meta.day:02}-"
                                                             f"{file_meta.hour:02}{file_meta.minute:02}{file_meta.second:02}{file_meta.milli_second:03}-"
                                                             f"s{file_meta.sequence_nr:03}-a{file_meta.sequence_axis}-"
                                                             f"f{file_meta.sequence_frequency_hz:03}-z{file_meta.sequence_zeta_em2:03}")

                if self.algorithm_d1 is not None:
                    fft_total, fft_processed, fft_skipped = self._fft_1d(self.algorithm_d1, samples, out_filename, self.output_overwrite)
                    skipped += 1 if fft_skipped > 0 else 0
                    processed += 1 if fft_processed == fft_total else 0

                else:
                    logging.info("nothing to do")

            logging.info(f"decompose runner traversed input files: total={total} processed={processed} skipped={skipped}")
            return 0, total, processed, skipped

        else:
            logging.info("nothing to do")
            return -1, total, processed, skipped
