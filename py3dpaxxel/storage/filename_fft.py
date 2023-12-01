from typing import Literal, Optional

from py3dpaxxel.storage.filename import timestamp, timestamp_regex


def generate_filename_for_fft(prefix_1: Optional[str],
                              prefix_2: Optional[str],
                              prefix_3: Optional[str],
                              sequence_nr: int,
                              axis: Literal["x", "y", "z"],
                              frequency: int,
                              zeta: int,
                              fft_axis: str,
                              ext: str = "tsv") -> str:
    pre_1 = f"{prefix_1}-" if prefix_1 and prefix_1 != "" else ""
    pre_2 = f"{prefix_2}-" if prefix_2 and prefix_2 != "" else ""
    pre_3 = f"{prefix_3}-" if prefix_3 and prefix_3 != "" else ""
    return f"{pre_1}{pre_2}{pre_3}{timestamp()}-s{sequence_nr:03}-a{axis}-f{frequency:03}-z{zeta:03}-{fft_axis}.{ext}"


def generate_filename_for_fft_regex(with_prefix_1: bool = True,
                                    with_prefix_2: bool = False,
                                    with_prefix_3: bool = False) -> str:
    pre_1_regex = r"(\w+)-" if with_prefix_1 else ""
    pre_2_regex = r"(\w+)-" if with_prefix_2 else ""
    pre_3_regex = r"(\w+)-" if with_prefix_3 else ""
    return pre_1_regex + pre_2_regex + pre_3_regex + timestamp_regex() + r"-s(\d{3})-a(\w{1})-f(\d{3})-z(\d{3})-([xyz]).(\w+)"
