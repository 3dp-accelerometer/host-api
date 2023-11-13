import os
from typing import Tuple, List, Literal, get_args


def convert_xy_pos_from_str(pos: str) -> Tuple[int, int]:
    x, y = pos.strip("\"").split(",")
    x = int(x)
    y = int(y)
    return x, y


def assert_uint_0_100(f: str) -> float:
    value = float(f)
    assert 0 <= value <= 100
    return value


def assert_uint16(n: str) -> int:
    value = int(n)
    assert 0 <= value <= 65536
    return value


def convert_uint16_from_str(n: str) -> int:
    return assert_uint16(n)


def path_exists_and_is_file(file_path: str) -> str | None:
    return file_path if os.path.isfile(file_path) else None


def convert_axis_from_str(axis_names: Literal["x", "y", "xy"]) -> List[Literal["x", "y"]]:
    x: Literal["x", "y"] | None = None if len(axis_names) < 1 else axis_names[0]
    y: Literal["x", "y"] | None = None if len(axis_names) < 2 else axis_names[1]

    literal = Literal["x", "y"]

    assert x in get_args(literal) if x is not None else True
    assert y in get_args(literal) if y is not None else True

    return [i for i in [x, y] if i is not None]
