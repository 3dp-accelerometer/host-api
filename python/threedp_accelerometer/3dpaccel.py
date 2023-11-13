#!/bin/env python3

import argparse
import logging
import sys

from controller.constants import OutputDataRate, Range, Scale
from log.log_levels import LogLevel
from threedp_accelerometer.cli import file_name
from threedp_accelerometer.cli.args import convert_uint16_from_str
from threedp_accelerometer.controller.runner import ControllerRunner


class Args:

    @staticmethod
    def default_filename() -> str:
        return file_name.generate_filename()

    def __init__(self) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(
            dest='command',
            title="command (required)",
            description="Run command with the loaded configuration.")

        sup = sub_parsers.add_parser(
            "device",
            help="device info",
            description="Retrieve device information.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-l", "--list",
            help="List attached devices.",
            action="store_true")
        grp.add_argument(
            "-r", "--reboot",
            help="Performs a device reboot (reset).",
            action="store_true")
        sup = sub_parsers.add_parser(
            "set",
            help="device setup",
            description="Configure output data rate, resolution and range.")

        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-o", "--outputdatarate",
            help="Set sampling rate.",
            choices=[e.name for e in OutputDataRate])
        grp.add_argument(
            "-s", "--scale",
            help="Set sampling resolution.",
            choices=[e.name for e in Scale])
        grp.add_argument(
            "-r", "--range",
            help="Set sampling range. ",
            choices=[e.name for e in Range])

        sup = sub_parsers.add_parser(
            "get",
            help="read device setup",
            description="Reads device parameters.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-o", "--outputdatarate",
            help="Read sampling rate.",
            action="store_true")
        grp.add_argument(
            "-s", "--scale",
            help="Read sampling resolution.",
            action="store_true")
        grp.add_argument(
            "-r", "--range",
            help="Read sampling range.",
            action="store_true")
        grp.add_argument(
            "-a", "--all",
            help="Read all parameter.",
            action="store_true")

        sup = sub_parsers.add_parser(
            "stream",
            help="start/stop streaming",
            description="Starts or stops data streaming from device.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-s", "--start",
            help="Starts streaming for n samples, If n=0 enables streaming until stop is requested (0 <= n <= UINT16_MAX).",
            type=convert_uint16_from_str,
            nargs='?',
            const=0)
        grp.add_argument(
            "-p", "--stop",
            help="Stops current stream.",
            action="store_true")

        sup = sub_parsers.add_parser(
            "decode",
            help="data decoding",
            description="Connects to device and decodes input stream. "
                        "The connection must be established before the data stream is started. "
                        "While decoding, subsequent script calls with \"stream\" and \"set\" commands are allowed.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-", "--stdout",
            help="Prints streamed data to stdout. Script does not finish when stream stops and waits for subsequent runs.",
            action="store_true")
        grp.add_argument(
            "-f", "--file",
            help="Writes streamed data to file. Script finishes when stream is stopped. "
                 "While decoding, simultaneous calls to output stream are allowed: start, stop and setup commands. "
                 f"Leave empty string for default fallback filename \"{self.default_filename}\".",
            type=str,
            nargs='?',
            const=self.default_filename)

        sub_group = self.parser.add_argument_group(
            "Flags",
            description="General flags applied to all commands.")
        sub_group.add_argument(
            "-l", "--log",
            help="Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            choices=[e.name for e in LogLevel],
            default="INFO")
        sub_group.add_argument(
            "-d", "--device",
            help="Specify the serial device to communicate with.",
            default="/dev/ttyACM0")

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner:

    def __init__(self) -> None:
        self._cli_args: Args = Args()
        logging.basicConfig(level=LogLevel[self.args.log].value)

    @property
    def args(self):
        return self._cli_args.args

    @property
    def parser(self):
        return self._cli_args.parser

    def run(self) -> int:
        ret = ControllerRunner(
            command=self.args.command,
            controller_serial_dev_name=self.args.device,
            controller_do_list_devices=self.args.list if hasattr(self.args, "list") else None,
            controller_do_reboot=self.args.reboot if hasattr(self.args, "reboot") else None,
            sensor_output_data_rate=OutputDataRate(self.args.outputdatarate) if hasattr(self.args, "outputdatarate") and self.args.outputdatarate is not None else None,
            sensor_scale=Scale(self.args.scale) if hasattr(self.args, "scale") and self.args.scale is not None else None,
            sensor_range=Range(self.args.range) if hasattr(self.args, "range") and self.args.range is not None else None,
            sensor_all_settings=self.args.all if hasattr(self.args, "all") else None,
            stream_start=self.args.start if hasattr(self.args, "start") else None,
            stream_stop=self.args.stop if hasattr(self.args, "stop") else None,
            stream_decode=self.args.decode if hasattr(self.args, "decode") else None,
            output_file=self.args.file if hasattr(self.args, "file") else None,
            output_stdout=self.args.stdout if hasattr(self.args, "stdout") else None).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
