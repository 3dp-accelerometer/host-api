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
        grp.add_argument("-l", "--list",
                         help="List attached devices.",
                         action="store_true")

        sup = sub_parsers.add_parser(
            "set",
            help="set sampling parameter",
            description="Configure output data rate, resolution and range.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-o", "--outputdatarate",
                         help="Set sampling rate.",
                         choices=[e.name for e in OutputDataRate])
        grp.add_argument("-s", "--scale",
                         help="Set sampling resolution.",
                         choices=[e.name for e in Scale])
        grp.add_argument("-r", "--range",
                         help="Set sampling range. ",
                         choices=[e.name for e in Range])

        sup = sub_parsers.add_parser("get",
                                     help="read config device status",
                                     description="Reads device parameters.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-o", "--outputdatarate",
                         help="Read sampling rate.",
                         action="store_true")
        grp.add_argument("-s", "--scale",
                         help="Read sampling resolution.",
                         action="store_true")
        grp.add_argument("-r", "--range",
                         help="Read sampling range.",
                         action="store_true")
        grp.add_argument("-a", "--all",
                         help="Read all parameter (-org).",
                         action="store_true")

        sup = sub_parsers.add_parser(
            "stream",
            help="enable disable data streaming",
            description="Will start or stop the acceleration data streaming.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-s", "--start",
                         help="Enables streaming.",
                         action="store_true")
        grp.add_argument("-p", "--stop",
                         help="Stops streaming.",
                         action="store_true")

        sub_group = self.parser.add_argument_group("Logging",
                                                   description="Manipulate the verbosity level.")
        grp = sub_group.add_mutually_exclusive_group()

        grp.add_argument("-l", "--log",
                         help="Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
                         choices=[e.name for e in LogLevel],
                         default="INFO")

        grp.add_argument("-d", "--device",
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
                    logging.info(f"{s.device} {s.manufacturer} {s.description} {s.hwid}")
            else:
                logging.warning("noting to do")

        if self.args.device not in [c.device for c in comports()]:
            logging.error(f"device {self.args.device} not found")
            return 1

        if self.args.command == "set":
            if self.args.outputdatarate:
                logging.info(f"send outputdatarate={self.args.outputdatarate}")
                with Adxl345(self.args.device) as sensor:
                    sensor.set_output_data_rate(OutputDataRate[self.args.outputdatarate])
            elif self.args.scale:
                logging.info(f"send scale={self.args.scale}")
                with Adxl345(self.args.device) as sensor:
                    sensor.set_scale(Scale[self.args.scale])
            elif self.args.range:
                logging.info(f"send range={self.args.range}")
                with Adxl345(self.args.device) as sensor:
                    sensor.set_range(Range[self.args.range])
            else:
                logging.warning("noting to do")
                return 1

        if self.args.command == "get":
            if self.args.outputdatarate:
                with Adxl345(self.args.device) as sensor:
                    logging.debug(f"request odr")
                    logging.info(f"odr={sensor.get_output_data_rate().name}")
            elif self.args.scale:
                logging.debug(f"request scale")
                with Adxl345(self.args.device) as sensor:
                    logging.info(f"scale={sensor.get_scale().name}")
            elif self.args.range:
                logging.debug(f"request range")
                with Adxl345(self.args.device) as sensor:
                    logging.info(f"range={sensor.get_range().name}")
            elif self.args.all:
                with Adxl345(self.args.device) as sensor:
                    logging.info(f"odr={sensor.get_output_data_rate().name}")
                    logging.info(f"scale={sensor.get_scale().name}")
                    logging.info(f"range={sensor.get_range().name}")
            else:
                logging.warning("noting to do")
                return 1

        if self.args.command == "stream":
            if self.args.start:
                logging.info("start")
            elif self.args.stop:
                logging.info("stop")
            else:
                logging.warning("noting to do")
                return 1

        return 0


if __name__ == "__main__":
    sys.exit(Runner().run())
