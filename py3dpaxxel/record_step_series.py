#!/bin/env python3

import argparse
import sys

from controller.constants import OutputDataRate
from py3dpaxxel.cli import args
from py3dpaxxel.log.setup import configure_logging
from py3dpaxxel.octoprint.remote_api import OctoRemoteApi
from py3dpaxxel.sampling_tasks.steps_series_runner import SamplingStepsSeriesRunner

configure_logging()


class Args:
    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Records a series of recording-steps samples while sending G-Code to the printer.")

        sub_group = self.parser.add_argument_group(
            "REST API",
            description="Octoprint arguments.")
        sub_group.add_argument(
            "--address",
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
            description="Trajectory settings")
        sub_group.add_argument(
            "--axis",
            help="Axis to move.",
            type=str,
            choices=["x", "y", "z", "xy", "xz", "yz", "xyz"],
            default="x")
        sub_group.add_argument(
            "--start",
            help="Start pont in mm to begin trajectory at.",
            type=args.convert_xyz_pos_from_str,
            default="\"200,140,20\"")
        sub_group.add_argument(
            "--distance",
            help="Distance in mm to travel back and forth.",
            type=int,
            default=20)
        sub_group.add_argument(
            "--repetitions",
            help="Repeat travel back and forth N times.",
            type=int,
            default=4)

        sub_group = self.parser.add_argument_group(
            "Task",
            description="Capturing task repetitions with different parameters")
        sub_group.add_argument(
            "--runs",
            help="Repeats the capturing task with same arguments R times.",
            type=int,
            default=1)
        sub_group.add_argument(
            "--fxstart",
            help="Start frequency in Hz. See https://marlinfw.org/docs/gcode/M593.html",
            type=args.assert_uint16,
            default="10")
        sub_group.add_argument(
            "--fxstop",
            help="Start frequency in Hz.",
            type=args.assert_uint16,
            default="80")
        sub_group.add_argument(
            "--fxstep",
            help="Frequency increment in Hz.",
            type=args.assert_uint16,
            default=10)
        sub_group.add_argument(
            "--zetastart",
            help="Zeta damping factor (times 100). See https://marlinfw.org/docs/gcode/M593.html",
            type=args.assert_uint_0_100,
            default=0)
        sub_group.add_argument(
            "--zetastop",
            help="Zeta damping factor (times 100).",
            type=args.assert_uint_0_100,
            default=25)
        sub_group.add_argument(
            "--zetastep",
            help="Zeta damping factor increment (times 100).",
            type=args.assert_uint_0_100,
            default=5)

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
            help="Duration in seconds the script waits until data is received (left unset or 0.0 waits forever). Raises exception otherwise.",
            type=float,
            default=0.0)
        sub_group.add_argument(
            "--dryrun",
            help=f"Pretends to run but does not invoke either Octoprint nor controller.",
            action="store_true")
        sub_group.add_argument(
            "--fileprefix",
            help=f"Specify prefix of output file (<prefix>-<run>-<timestamp>.tsv)",
            type=str,
            default="octo-capture")
        sub_group.add_argument(
            "--directory",
            help=f"Output path.",
            type=args.path_exists_and_is_dir,
            default="./data/")

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
        octo_api = OctoRemoteApi(self.args.key, self.args.address, self.args.port, self.args.dryrun)

        ret = SamplingStepsSeriesRunner(
            octoprint_api=octo_api,
            controller_serial_device=self.args.device,
            controller_record_timelapse_s=self.args.timelapse,
            controller_decode_timeout_s=self.args.timeout,
            sensor_odr=OutputDataRate[self.args.outputdatarate],
            gcode_start_point_mm=self.args.start,
            gcode_axis=args.convert_axis_from_str(self.args.axis),
            gcode_distance_mm=self.args.distance,
            gcode_repetitions=self.args.repetitions,
            runs=self.args.runs,
            fx_start=self.args.fxstart,
            fx_stop=self.args.fxstop,
            fx_step=self.args.fxstep,
            zeta_start=self.args.zetastart,
            zeta_stop=self.args.zetastop,
            zeta_step=self.args.zetastep,
            output_file_prefix=self.args.fileprefix,
            output_dir=self.args.directory,
            do_dry_run=self.args.dryrun).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
