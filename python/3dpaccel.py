#!/bin/env python3

import argparse
import logging
import sys
from enum import Enum

from serial.tools.list_ports import comports

from lib.device_constants import OutputDataRate, Range, Scale
from lib.device_io import Adxl345


class LogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Args:
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
            help="set sampling parameter",
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
            help="read config device status",
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
            help="Read all parameter (-org).",
            action="store_true")

        sup = sub_parsers.add_parser(
            "stream",
            help="enable disable data streaming",
            description="Will start or stop the acceleration data streaming.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument(
            "-s", "--start",
            help="Enables streaming until stop is rquested (--stop).",
            action="store_true")

        def max_n(n: str) -> int | None:
            value = int(n)
            return value if value <= 65536 else None

        grp.add_argument(
            "-n", "--startn",
            help="Enables streaming for N samples (N=UINT16_MAX).",
            type=max_n)
        grp.add_argument(
            "-p", "--stop",
            help="Stops streaming started with --start.",
            action="store_true")

        sub_group = self.parser.add_argument_group(
            "Logging",
            description="Manipulate the verbosity level.")
        grp = sub_group.add_mutually_exclusive_group()

        grp.add_argument(
            "-l", "--log",
            help="Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
            choices=[e.name for e in LogLevel],
            default="INFO")

        grp.add_argument(
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
        if not self.args.command:
            self.parser.print_help()
            return 1

        if self.args.command == "device":
            if self.args.list:
                for s in comports():
                    logging.info("%s %s %s %s", s.device, s.manufacturer, s.description, s.hwid)
            elif self.args.reboot:
                logging.info("device reboot")
                with Adxl345(self.args.device) as sensor:
                    sensor.reboot()
            else:
                logging.warning("noting to do")

        # elif self.args.device not in [c.device for c in comports()]:
        #    logging.error("device %s not found", self.args.device)
        #    return 1

        elif self.args.command == "set":
            if self.args.outputdatarate:
                logging.info("send outputdatarate=%s", self.args.outputdatarate)
                with Adxl345(self.args.device) as sensor:
                    sensor.set_output_data_rate(OutputDataRate[self.args.outputdatarate])
            elif self.args.scale:
                logging.info("send scale=%s", self.args.scale)
                with Adxl345(self.args.device) as sensor:
                    sensor.set_scale(Scale[self.args.scale])
            elif self.args.range:
                logging.info("send range=%s", self.args.range)
                with Adxl345(self.args.device) as sensor:
                    sensor.set_range(Range[self.args.range])
            else:
                logging.warning("noting to do")
                return 1

        elif self.args.command == "get":
            if self.args.outputdatarate:
                logging.debug("request odr")
                with Adxl345(self.args.device) as sensor:
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
            elif self.args.scale:
                logging.debug("request scale")
                with Adxl345(self.args.device) as sensor:
                    logging.info("scale=%s", sensor.get_scale().name)
            elif self.args.range:
                logging.debug("request range")
                with Adxl345(self.args.device) as sensor:
                    logging.info("range=%s", sensor.get_range().name)
            elif self.args.all:
                with Adxl345(self.args.device) as sensor:
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
                    logging.info("scale=%s", sensor.get_scale().name)
                    logging.info("range=%s", sensor.get_range().name)
            else:
                logging.warning("noting to do")
                return 1

        elif self.args.command == "stream":
            if self.args.start:
                logging.info("sampling start")
                with Adxl345(self.args.device) as sensor:
                    sensor.start_sampling()
            elif self.args.startn:
                logging.info("sampling start n=%s", self.args.startn)
                with Adxl345(self.args.device) as sensor:
                    sensor.start_sampling_n(self.args.startn)
            elif self.args.stop:
                logging.info("sampling stop")
                with Adxl345(self.args.device) as sensor:
                    sensor.stop_sampling()
            else:
                logging.warning("noting to do")
                return 1

        return 0


if __name__ == "__main__":
    sys.exit(Runner().run())
