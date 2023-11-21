from datetime import datetime
from typing import Literal, Union

_filename_timestamp_pattern: str = "%Y%m%d-%H%M%S%f"


def _timestamp() -> str:
    return datetime.now().strftime(_filename_timestamp_pattern)[:-3]


def generate_filename(prefix: str = "stream", ext: str = "tsv") -> str:
    default_filename = f"{prefix}-{_timestamp()}.{ext}"
    return default_filename


def generate_filename_for_run(prefix: Union[str, None], sequence_nr: int, axis: Literal["x", "y", "z"], frequency: int, zeta: int, ext: str = "tsv") -> str:
    pre = f"{prefix}-" if prefix != "" else ""
    return f"{pre}{_timestamp()}-s{sequence_nr:03}-a{axis}-f{frequency:03}-z{zeta:03}.{ext}"
