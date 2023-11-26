#!/bin/env python3

import argparse
import sys
from typing import Optional

from py3dpaxxel.cli import args
from py3dpaxxel.data_decomposition.decompose_algorithms import DecomposeFftAlgorithms1D
from py3dpaxxel.data_decomposition.decompose_runner import DataDecomposeRunner
from py3dpaxxel.log.setup import configure_logging

configure_logging()


def args_for_sphinx():
    return Args().parser


class Args:
    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(
            dest='command',
            title="command (required)",
            description="Run specified sub-command.")

        sup = sub_parsers.add_parser(
            "algo",
            help="FFT algorithm (1-D)",
            description="FFT Algorithm applied to input data.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-1", "--d1",
            help="Performs FFT 1D algorithms: discrete 1D, discrete 1D with Blackman window.",
            type=str,
            nargs='?',
            choices=[k for k in DecomposeFftAlgorithms1D().algorithms.keys()],
            const=[k for k in DecomposeFftAlgorithms1D().algorithms.keys()][0])

        sub_group = self.parser.add_argument_group(
            "Flags",
            description="General flags applied to all commands.")

        sub_group.add_argument(
            "--indir",
            help="Input path.",
            type=args.path_exists_and_is_dir,
            default="./test_data/")
        sub_group.add_argument(
            "--infileprefix",
            help="Prefix of input files.",
            type=str,
            default="test")
        sub_group.add_argument(
            "--outdir",
            help="Output path.",
            type=args.path_exists_and_is_dir,
            default="./test_data/")
        sub_group.add_argument(
            "--outfileprefix",
            help="Prefix of output files.",
            type=str,
            default="fft")
        sub_group.add_argument(
            "--force",
            help="Overwrite existing output files.",
            action="store_true")

        self.args: Optional[argparse.Namespace] = None

    def parse(self) -> "Args":
        self.args = self.parser.parse_args()
        return self


class Runner:

    def __init__(self) -> None:
        self._cli_args: Args = Args().parse()

    @property
    def args(self):
        return self._cli_args.args

    @property
    def parser(self):
        return self._cli_args.parser

    def run(self) -> int:
        if not self.args:
            self.parser.print_help()
            return 1

        ret = DataDecomposeRunner(
            command=self.args.command,
            input_dir=self.args.indir,
            input_file_prefix=self.args.infileprefix,
            algorithm_d1=self.args.d1,
            output_dir=self.args.outdir,
            output_file_prefix=self.args.outfileprefix,
            output_overwrite=self.args.force).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
