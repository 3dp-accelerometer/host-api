#!/bin/env python3

import argparse
import sys

from py3dpaxxel.data_decomposition.datavis_algorithms import FftAlgorithms1D, FftAlgorithms2D, FftAlgorithms3D
from py3dpaxxel.data_decomposition.runner import DataVisualizerRunner
from py3dpaxxel.log.setup import configure_logging

configure_logging()


class Args:
    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(
            dest='command',
            title="command (required)",
            description="Run command with the loaded configuration.")

        sup = sub_parsers.add_parser(
            "algo",
            help="FFT algorithm (1-D, 2-D N-D)",
            description="FFT Algorithm applied to input data.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-1", "--d1",
            help="Performs FFT 1D algorithms: discrete 1D, discrete 1D with Blackman window or both.",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms1D().algorithms.keys()],
            const=[k for k in FftAlgorithms1D().algorithms.keys()][0])
        grp.add_argument(
            "-2", "--d2",
            help="FFT 2D algorithms: no algorithm implemented yet (TODO)",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms2D().algorithms.keys()],
            const=[k for k in FftAlgorithms2D().algorithms.keys()][0])
        grp.add_argument(
            "-3", "--d3",
            help="FFT 3D algorithms: compute trajectory from acceleration. Requires offset, gain and orientation calibration.",
            type=str,
            nargs='?',
            choices=["all"] + [k for k in FftAlgorithms3D().algorithms.keys()],
            const=[k for k in FftAlgorithms3D().algorithms.keys()][0])

        sub_group = self.parser.add_argument_group(
            "Flags",
            description="General flags applied to all commands.")
        sub_group.add_argument(
            "-f", "--file",
            help="Input file name or regexp-pattern. Examples: \"example.tsv\", \"data/\",...)",
            type=str,
            default="example.tsv")
        sub_group.add_argument(
            "-p", "--plot",
            help="Visualizes data",
            action="store_true")
        sub_group.add_argument(
            "-s", "--save",
            help="Saves plots as PNG format.",
            action="store_true")

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner:

    def __init__(self) -> None:
        self._cli_args: Args = Args()

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

        ret = DataVisualizerRunner(
            command=self.args.command,
            input_filename=self.args.file,
            algorithm_d1=self.args.d1,
            algorithm_d2=self.args.d2,
            algorithm_d3=self.args.d3,
            output_save=self.args.save,
            output_plot=self.args.plot).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
