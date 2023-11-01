#!/bin/env python3

import argparse
import logging
import sys
from enum import Enum

from serial.tools.list_ports import comports

from lib.device_io import CdcSerial
from lib.device_types import OutputDataRate, Range, TransportHeaderId, Scale


class LogLevel(Enum):
    i = "i"  # info
    v = "v"  # info, verbose
    d = "d"  # info, verbose, debug


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
                         help="Set the logging level. Info (I): lesser logs; "
                              "Verbose (V): more logs; Debug (D): all logs.",
                         choices=[e.name for e in LogLevel])

        grp.add_argument("-d", "--device",
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
        if not self.args.command:
            self.parser.print_help()
            return 1

        # setup log levels
        def disable_levels(levels):
            for log_level in levels:
                logging.disable(log_level)

        {
            LogLevel.i.value: lambda: disable_levels([logging.DEBUG, logging.WARNING]),
            LogLevel.v.value: lambda: disable_levels([logging.WARNING]),
            LogLevel.d.value: lambda: disable_levels([]),
            None: lambda: disable_levels([]),
        }[self.args.log]()

        if self.args.command == "device":
            if self.args.list:
                for s in comports():
                    print(f"{s.device} {s.manufacturer} {s.description} {s.hwid}")
            else:
                logging.warning("noting to do")

        if self.args.device not in [c.device for c in comports()]:
            logging.error(f"device {self.args.device} not found")
            return 1

        if self.args.command == "set":
            if self.args.outputdatarate:
                print("set odr")
            elif self.args.scale:
                print("set scale")
            elif self.args.range:
                print("set range")
            else:
                logging.warning("noting to do")
                return 1

        if self.args.command == "get":
            if self.args.outputdatarate:
                with CdcSerial(self.args.device, 0.1) as s:
                    r = s.send_request(TransportHeaderId.GetOutputDataRate, 1)[0]
                    print(f"odr={OutputDataRate(r).name}")
            elif self.args.scale:
                with CdcSerial(self.args.device, 0.1) as s:
                    r = s.send_request(TransportHeaderId.GetScale, 1)[0]
                    print(f"scale={Scale(r).name}")
            elif self.args.range:
                with CdcSerial(self.args.device, 0.1) as s:
                    r = s.send_request(TransportHeaderId.GetRange, 1)[0]
                    print(f"range={Range(r).name}")
            elif self.args.all:
                with CdcSerial(self.args.device, 0.1) as s:
                    r = s.send_request(TransportHeaderId.GetOutputDataRate, 1)[0]
                    print(f"odr={OutputDataRate(r).name}")
                    r = s.send_request(TransportHeaderId.GetScale, 1)[0]
                    print(f"scale={Scale(r).name}")
                    r = s.send_request(TransportHeaderId.GetRange, 1)[0]
                    print(f"range={Range(r).name}")
            else:
                logging.warning("noting to do")
                return 1

        if self.args.command == "stream":
            if self.args.start:
                print("start")
            elif self.args.stop:
                print("stop")
            else:
                logging.warning("noting to do")
                return 1

        return 0


if __name__ == "__main__":
    sys.exit(Runner().run())
