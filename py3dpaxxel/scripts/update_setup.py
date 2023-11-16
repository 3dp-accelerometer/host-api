#!/bin/env python3

import os

from poetry2setup import build_setup_py


def update():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "..", "..", "setup.py"), "w") as setup_py:
        setup_py.write(build_setup_py().decode("utf8"))
    return 0


if __name__ == "__main__":
    update()
