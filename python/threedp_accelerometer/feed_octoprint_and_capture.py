#!/bin/env python3

import argparse
import logging
import sys

from cli import args
from controller.constants import OutputDataRate
from log.log_levels import LogLevel
from octoprint.api import OctoApi
from threedp_accelerometer.cli import file_name
from threedp_accelerometer.octoprint.runner import SamplingJobRunner


class Args:

    @staticmethod
    def default_filename() -> str:
        return file_name.generate_filename(prefix="op-capture")

    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        sub_group = self.parser.add_argument_group(
            "REST API",
            description="Octoprint arguments.")
        sub_group.add_argument(
            "-a", "--address",
            help="OctoPrint address",
            required=True)
        sub_group.add_argument(
            "-p", "--port",
            help="OctoPrint port (default 80)",
            type=int,
            default=80)
        sub_group.add_argument(
            "-k", "--key",
            help="OctoPrint API key.",
            type=str,
            default=80)

        sub_group = self.parser.add_argument_group(
            "Trajectory",
            description="Trajectory generator")
        sub_group.add_argument(
            "-x", "--axis",
            help="Axis to move.",
            type=str,
            choices=["x", "y"],
            default="x")
        sub_group.add_argument(
            "-b", "--begin",
            help="Start pont in mm to begin trajectory at,",
            type=args.convert_xy_pos_from_str,
            default="\"200,140\"")
        sub_group.add_argument(
            "-e", "--extragcode",
            help="Extra G-Code to send before trajectory (i.e. input shaping: \"M593 X F30 D0.15\").",
            type=str,
            default="\"\"")
        sub_group.add_argument(
            "-s", "--distance",
            help="Distance in mm to travel back and forth.",
            type=int,
            default=20)
        sub_group.add_argument(
            "-n", "--repetitions",
            help="Repeat travel back and forth N times.",
            type=int,
            default=4)
        sub_group.add_argument(
            "-g", "--gostart",
            help="Go to start position first, then start repetitions.",
            action="store_true")
        sub_group.add_argument(
            "-u", "--returnstart",
            help="Return to start point after last repetition.",
            action="store_true")
        sub_group.add_argument(
            "-m", "--autohome",
            help="Perform auto homing before trajectory.",
            action="store_true")
        sub_group = self.parser.add_argument_group(
            "Controller",
            description="Acceleration microcontroller arguments.")
        sub_group.add_argument(
            "-d", "--device",
            help="Controllers serial device node to communicate with.",
            default="/dev/ttyACM0")
        sub_group.add_argument(
            "-o", "--outputdatarate",
            help="Set specified sampling rate before sending G-Code.",
            choices=[e.name for e in OutputDataRate],
            default=OutputDataRate.ODR3200.name)
        sub_group.add_argument(
            "-t", "--timelapse",
            help="Timespan to record captured samples in seconds.",
            type=float,
            default=1.0)

        sub_group = self.parser.add_argument_group(
            "Output",
            description="Output arguments.")
        mux_grp = sub_group.add_mutually_exclusive_group()
        mux_grp.add_argument(
            "-", "--stdout",
            help="Prints streamed data to stdout. Script does not finish when stream stops and waits for subsequent runs.",
            action="store_true")
        mux_grp.add_argument(
            "-f", "--file",
            help=f"Specify output file (*.tsv). Leave empty for default filename.",
            type=str,
            nargs='?',
            const=self.default_filename)
        sub_group.add_argument(
            "-l", "--log",
            help="Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            choices=[e.name for e in LogLevel],
            default="INFO")

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner:
    def __init__(self):
        self._cli_args: Args = Args()
        logging.basicConfig(level=LogLevel[self.args.log].value)
        self.octo_api: OctoApi | None = None

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

        ret =  SamplingJobRunner(
            input_serial_device=self.args.device,
            intput_sensor_odr=OutputDataRate[self.args.outputdatarate],
            record_timelapse_s=self.args.timelapse,
            output_file_name=self.args.file,
            octoprint_address=self.args.address,
            octoprint_port=self.args.port,
            octoprint_api_key=self.args.key,
            gcode_start_point_mm=self.args.begin,
            gcode_extra_gcode=self.args.extragcode,
            gcode_axis=self.args.axis,
            gcode_distance_mm=self.args.distance,
            gcode_repetitions=self.args.repetitions,
            gcode_go_start=self.args.gostart,
            gcode_return_start=self.args.returnstart,
            gcode_auto_home=self.args.autohome).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
