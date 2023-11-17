#!/bin/env python3

import argparse
import sys
from typing import Literal

from controller.constants import OutputDataRate, Range, Scale
from py3dpaxxel.cli import filename
from py3dpaxxel.cli.args import convert_uint16_from_str
from py3dpaxxel.controller.runner import ControllerRunner
from py3dpaxxel.log.setup import configure_logging

configure_logging()


class Args:

    @staticmethod
    def default_filename() -> str:
        return filename.generate_filename()

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
            help="List attached devices (human readable).",
            action="store_true")
        grp.add_argument(
            "-j", "--json",
            help="List attached devices (machine readable as JSON).",
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
            "-d", "--device",
            help="Specify the serial device to communicate with.",
            default="/dev/ttyACM0")

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
        command = self.args.command

        controller_serial_dev_name = self.args.device
        controller_do_list_devices: Literal["h", "j"] = "h" if hasattr(self.args, "list") and self.args.list else "j" if hasattr(self.args, "json") and self.args.json else None
        controller_do_reboot = self.args.reboot if hasattr(self.args, "reboot") else None

        sensor_set_output_data_rate = OutputDataRate[self.args.outputdatarate] if self.args.command == "set" and hasattr(self.args,
                                                                                                                         "outputdatarate") and self.args.outputdatarate is not None else None
        sensor_set_scale = Scale[self.args.scale] if self.args.command == "set" and hasattr(self.args, "scale") and self.args.scale is not None else None
        sensor_set_range = Range[self.args.range] if self.args.command == "set" and hasattr(self.args, "range") and self.args.range is not None else None
        sensor_get_output_data_rate = self.args.outputdatarate if self.args.command == "get" and hasattr(self.args, "outputdatarate") else None
        sensor_get_scale = self.args.scale if self.args.command == "get" and hasattr(self.args, "scale") else None
        sensor_get_range = self.args.range if self.args.command == "get" and hasattr(self.args, "range") else None
        sensor_get_all_settings = self.args.all if self.args.command == "get" and hasattr(self.args, "all") else None

        stream_start = self.args.start if hasattr(self.args, "start") else None
        stream_stop = self.args.stop if hasattr(self.args, "stop") else None
        stream_decode = self.args.decode if hasattr(self.args, "decode") else None

        output_file = self.args.file if hasattr(self.args, "file") else None
        output_stdout = self.args.stdout if hasattr(self.args, "stdout") else None

        ret = ControllerRunner(
            command=command,
            controller_serial_dev_name=controller_serial_dev_name,
            controller_do_list_devices=controller_do_list_devices,
            controller_do_reboot=controller_do_reboot,
            sensor_set_output_data_rate=sensor_set_output_data_rate,
            sensor_set_scale=sensor_set_scale,
            sensor_set_range=sensor_set_range,
            sensor_get_output_data_rate=sensor_get_output_data_rate,
            sensor_get_scale=sensor_get_scale,
            sensor_get_range=sensor_get_range,
            sensor_get_all_settings=sensor_get_all_settings,
            stream_start=stream_start,
            stream_stop=stream_stop,
            stream_decode=stream_decode,
            output_file=output_file,
            output_stdout=output_stdout).run()

        if ret == -1:
            self.parser.print_help()
        return ret


if __name__ == "__main__":
    sys.exit(Runner().run())
