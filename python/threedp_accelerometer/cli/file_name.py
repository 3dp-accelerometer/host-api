from datetime import datetime
from typing import Literal

_file_name_timestamp_pattern: str = "%Y-%m-%d-%H%M%S"


def generate_filename(prefix: str = "stream", ext: str = "tsv") -> str:
    timestamp = datetime.now().strftime(_file_name_timestamp_pattern)
    default_filename = f"{prefix}-{timestamp}.{ext}"
    return default_filename


def generate_filename_for_run(prefix: str | None, run_nr: int, axis: Literal["x", "y"], frequency: int, zeta: int, ext: str = "tsv") -> str:
    timestamp = datetime.now().strftime(_file_name_timestamp_pattern)
    pre = f"{prefix}-" if prefix != "" else ""
    return f"{pre}r{run_nr:03}-{axis}-f{frequency:03}-z{zeta:03}-{timestamp}.{ext}"
