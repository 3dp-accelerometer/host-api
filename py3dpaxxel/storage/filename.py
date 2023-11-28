from datetime import datetime
from typing import Literal, Optional

_filename_timestamp_pattern: str = "%Y%m%d-%H%M%S%f"
"""example: 20231110-181020345 is equivalent to 2023 Nov 10, 18:10:20.345"""


def _timestamp() -> str:
    return datetime.now().strftime(_filename_timestamp_pattern)[:-3]


def _timestamp_regex() -> str:
    return r"(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})(\d{3})"


def generate_filename(prefix: str = "stream", ext: str = "tsv") -> str:
    default_filename = f"{prefix}-{_timestamp()}.{ext}"
    return default_filename


def generate_filename_regex() -> str:
    return r"(\w+)-" + _timestamp_regex() + r".(\w+)"


def generate_filename_for_run(prefix: Optional[str], prefix_2: Optional[str], sequence_nr: int, axis: Literal["x", "y", "z"], frequency: int, zeta: int, ext: str = "tsv") -> str:
    pre_1 = f"{prefix}-" if prefix and prefix != "" else ""
    pre_2 = f"{prefix_2}-" if prefix_2 and prefix_2 != "" else ""
    return f"{pre_1}{pre_2}{_timestamp()}-s{sequence_nr:03}-a{axis}-f{frequency:03}-z{zeta:03}.{ext}"


def generate_filename_for_run_regex(with_prefix_1: bool = True, with_prefix_2: bool = False) -> str:
    pre_1_regex = r"(\w+)-" if with_prefix_1 else ""
    pre_2_regex = r"(\w+)-" if with_prefix_2 else ""
    return pre_1_regex + pre_2_regex + _timestamp_regex() + r"-s(\d{3})-a(\w{1})-f(\d{3})-z(\d{3}).(\w+)"


def generate_filename_for_fft_regex(with_prefix_1: bool = True, with_prefix_2: bool = False) -> str:
    pre_1_regex = r"(\w+)-" if with_prefix_1 else ""
    pre_2_regex = r"(\w+)-" if with_prefix_2 else ""
    return pre_1_regex + pre_2_regex + _timestamp_regex() + r"-s(\d{3})-a(\w{1})-f(\d{3})-z(\d{3})-([xyz]).(\w+)"
