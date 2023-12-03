from datetime import datetime

filename_timestamp_pattern: str = "%Y%m%d-%H%M%S%f"
"""example: 20231110-181020345 is equivalent to 2023 Nov 10, 18:10:20.345"""


def timestamp() -> str:
    return datetime.now().strftime(filename_timestamp_pattern)[:-3]


def timestamp_from_args(year: int, month: int, day: int, hour: int, minute: int, second: int, milli_second: int) -> str:
    return f"{year:04}{month:02}{day:02}-{hour:02}{minute:02}{second:02}{milli_second:03}"


def timestamp_regex() -> str:
    return r"(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})(\d{3})"


def generate_filename(prefix: str = "stream", ext: str = "tsv") -> str:
    default_filename = f"{prefix}-{timestamp()}.{ext}"
    return default_filename
