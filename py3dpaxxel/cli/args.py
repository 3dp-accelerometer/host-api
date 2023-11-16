import os
from typing import Tuple, List, Literal, Union


def convert_xyz_pos_from_str(pos: str) -> Tuple[int, int, int]:
    x, y, z = pos.strip("\"").split(",")
    x = int(x)
    y = int(y)
    z = int(z)
    return x, y, z


def assert_uint_0_100(f: str) -> int:
    value = int(f)
    assert 0 <= value <= 100
    return value


def assert_uint16(n: str) -> int:
    value = int(n)
    assert 0 <= value <= 65536
    return value


def convert_uint16_from_str(n: str) -> int:
    return assert_uint16(n)


def path_exists_and_is_file(file_path: str) -> str:
    assert os.path.isfile(file_path), f"file {file_path} does not exist"
    return file_path


def path_exists_and_is_dir(file_path: str) -> str:
    assert os.path.isdir(file_path), f"directory {file_path} does not exist"
    return file_path


def convert_axis_from_str(axis_names: Literal["x", "y", "z", "xy", "xz", "yz", "xyz"]) -> List[Literal["x", "y", "z"]]:
    x: Union[Literal["x", "y", "z"], None] = "x" if "x" in axis_names else None
    y: Union[Literal["x", "y", "z"], None] = "y" if "y" in axis_names else None
    z: Union[Literal["x", "y", "z"], None] = "z" if "z" in axis_names else None

    return [i for i in [x, y, z] if i is not None]
