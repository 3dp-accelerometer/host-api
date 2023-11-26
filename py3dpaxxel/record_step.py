#!/bin/env python3

import argparse
import sys
from typing import Optional

from py3dpaxxel.cli import args
from py3dpaxxel.cli import filename
from py3dpaxxel.controller.constants import OutputDataRate
from py3dpaxxel.log.setup import configure_logging
from py3dpaxxel.octoprint.api import OctoApi
from py3dpaxxel.octoprint.remote_api import OctoRemoteApi
from py3dpaxxel.sampling_tasks.steps_runner import SamplingStepsRunner

configure_logging()


def args_for_sphinx():
    return Args().parser


class Args:

    @staticmethod
    def default_filename() -> str:
        return filename.generate_filename(prefix="op-capture")

    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Records acceleration while sending (G-Code) to the printer.")

        sub_group = self.parser.add_argument_group(
            "REST API",
            description="Octoprint arguments.")
        sub_group.add_argument("--address",
                               help="OctoPrint address",
                               required=True)
        sub_group.add_argument(
            "--port",
            help="OctoPrint port (default 80)",
            type=int,
            default=80)
        sub_group.add_argument(
            "--key",
            help="OctoPrint API key.",
            type=str,
            default=80)

        sub_group = self.parser.add_argument_group(
            "Trajectory",
            description="Trajectory generator")
        sub_group.add_argument(
            "--axis",
            help="Axis to move.",
            type=str,
            choices=["x", "y", "z"],
            default="x")
        sub_group.add_argument(
            "--start",
            help="Start point in mm to begin trajectory at.",
            type=args.convert_xyz_pos_from_str,
            default="\"200,140,20\"")
        sub_group.add_argument(
            "--extragcode",
            help="Extra G-Code to send before trajectory (i.e. input shaping: \"M593 X F30 D0.15\").",
            type=str,
            default="\"\"")
        sub_group.add_argument(
            "--distance",
            help="Distance in mm to travel back and forth.",
            type=int,
            default=20)
        sub_group.add_argument(
            "--stepcount",
            help="Repeat travel pattern stepcount-times.",
            type=int,
            default=4)
        sub_group.add_argument(
            "--gostart",
            help="Go to start position first, then start repetitions.",
            action="store_true")
        sub_group.add_argument(
            "--returnstart",
            help="Return to start point after last repetition.",
            action="store_true")
        sub_group.add_argument(
            "--autohome",
            help="Perform auto homing before trajectory.",
            action="store_true")
        sub_group = self.parser.add_argument_group(
            "Controller",
            description="Acceleration microcontroller arguments.")
        sub_group.add_argument(
            "--device",
            help="Controllers serial device node to communicate with.",
            default="/dev/ttyACM0")
        sub_group.add_argument(
            "--outputdatarate",
            help="Set specified sampling rate before sending G-Code.",
            choices=[e.name for e in OutputDataRate],
            default=OutputDataRate.ODR3200.name)
        sub_group.add_argument(
            "--timelapse",
            help="Timespan to record captured samples in seconds.",
            type=float,
            default=1.0)

        sub_group = self.parser.add_argument_group(
            "Output",
            description="Output arguments.")
        sub_group.add_argument(
            "--timeout",
            help="Duration in seconds the script waits until data is received (0.0 waits forever). Raises exception otherwise.",
            type=float,
            default=0.0)
        sub_group.add_argument(
            "--dryrun",
            help="Pretends to run but does not invoke either Octoprint nor controller.",
            action="store_true")
        mux_grp = sub_group.add_mutually_exclusive_group()
        mux_grp.add_argument(
            "-", "--stdout",
            help="Prints streamed data to stdout. Script does not finish when stream stops and waits for subsequent runs.",
            action="store_true")
        mux_grp.add_argument(
            "--file",
            help="Specify output file (*.tsv). Leave empty for default filename.",
            type=str,
            nargs='?',
            const=self.default_filename)

        self.args: Optional[argparse.Namespace] = None

    def parse(self) -> "Args":
        self.args = self.parser.parse_args()
        return self


class Runner:

    def __init__(self) -> None:
        self._cli_args: Args = Args().parse()
        self.octo_api: Optional[OctoApi] = None

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

        if self.args.stdout:
            self.args.file = None

        octo_api = OctoRemoteApi(self.args.key, self.args.address, self.args.port, self.args.dryrun)

        ret = SamplingStepsRunner(
            input_serial_device=self.args.device,
            intput_sensor_odr=OutputDataRate[self.args.outputdatarate],
            record_timelapse_s=self.args.timelapse,
            record_timeout_s=self.args.timeout,
            output_filename=self.args.file,
            octoprint_api=octo_api,
            gcode_start_point_mm=self.args.start,
            gcode_extra_gcode=self.args.extragcode,
            gcode_axis=self.args.axis,
            gcode_distance_mm=self.args.distance,
            gcode_step_repeat_count=self.args.stepcount,
            gcode_go_start=self.args.gostart,
            gcode_return_start=self.args.returnstart,
            gcode_auto_home=self.args.autohome,
            do_dry_run=self.args.dryrun)()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
