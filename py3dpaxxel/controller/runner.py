import json
import logging
from typing import Literal, Optional

from .api import Py3dpAxxel
from .constants import OutputDataRate, Range, Scale


class ControllerRunner:

    def __init__(
            self,
            command: Optional[str],
            controller_serial_dev_name: Optional[str],
            controller_do_list_devices: Optional[Literal["h", "j"]],
            controller_do_reboot: Optional[bool],
            sensor_set_output_data_rate: Optional[OutputDataRate],
            sensor_set_scale: Optional[Scale],
            sensor_set_range: Optional[Range],
            sensor_get_firmware_version: bool,
            sensor_get_output_data_rate: bool,
            sensor_get_scale: bool,
            sensor_get_range: bool,
            sensor_get_all_settings: bool,
            stream_start: Optional[int],
            stream_stop: Optional[bool],
            stream_decode: Optional[bool],
            stream_decode_timeout_s: Optional[float],
            stream_wait: bool,
            output_file: Optional[str],
            output_stdout: Optional[bool],
    ) -> None:
        self.command: Optional[str] = command
        self.controller_serial_dev_name: Optional[str] = controller_serial_dev_name
        self.controller_do_list_devices: Optional[Literal["h", "j"]] = controller_do_list_devices
        self.controller_do_reboot: Optional[bool] = controller_do_reboot
        self.sensor_set_output_data_rate: Optional[OutputDataRate] = sensor_set_output_data_rate
        self.sensor_set_scale: Optional[Scale] = sensor_set_scale
        self.sensor_set_range: Optional[Range] = sensor_set_range
        self.sensor_get_firmware_version: bool = sensor_get_firmware_version
        self.sensor_get_output_data_rate: bool = sensor_get_output_data_rate
        self.sensor_get_scale: bool = sensor_get_scale
        self.sensor_get_range: bool = sensor_get_range
        self.sensor_get_all_settings: bool = sensor_get_all_settings
        self.stream_start: Optional[int] = stream_start
        self.stream_stop: Optional[bool] = stream_stop
        self.stream_decode: Optional[bool] = stream_decode
        self.stream_wait: bool = stream_wait
        self.output_file: Optional[str] = output_file
        self.output_stdout: Optional[bool] = output_stdout
        self.stream_decode_timeout_s: float = 0.0 if stream_decode_timeout_s is None else stream_decode_timeout_s

    def run(self) -> int:
        if not self.command:
            return -1

        if self.command == "device":
            if self.controller_do_list_devices:
                if "j" == self.controller_do_list_devices:
                    print(json.dumps(Py3dpAxxel.get_devices_dict(), indent=2))
                elif "h" == self.controller_do_list_devices:
                    _x = [print(d) for d in Py3dpAxxel.get_devices_list_human_readable()]

            elif self.controller_do_reboot:
                logging.info("device reboot")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.reboot()
            else:
                logging.warning("noting to do")

        elif self.command == "set":
            if self.sensor_set_output_data_rate:
                logging.info("send outputdatarate=%s", self.sensor_set_output_data_rate.name)
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.set_output_data_rate(self.sensor_set_output_data_rate)
            elif self.sensor_set_scale:
                logging.info("send scale=%s", self.sensor_set_scale.name)
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.set_scale(self.sensor_set_scale)
            elif self.sensor_set_range:
                logging.info("send range=%s", self.sensor_set_range.name)
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.set_range(self.sensor_set_range)
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "get":
            if self.sensor_get_firmware_version:
                logging.debug("request firmware version")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    logging.info("version=%s", sensor.get_firmware_version().string)
            elif self.sensor_get_output_data_rate:
                logging.debug("request odr")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
            elif self.sensor_get_scale:
                logging.debug("request scale")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    logging.info("scale=%s", sensor.get_scale().name)
            elif self.sensor_get_range:
                logging.debug("request range")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    logging.info("range=%s", sensor.get_range().name)
            elif self.sensor_get_all_settings:
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    logging.info("version=%s", sensor.get_firmware_version().string)
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
                    logging.info("scale=%s", sensor.get_scale().name)
                    logging.info("range=%s", sensor.get_range().name)
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "stream":
            if self.stream_start is not None:
                logging.info("sampling start n=%s", self.stream_start)
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.start_sampling(self.stream_start)
            elif self.stream_stop:
                logging.info("sampling stop")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.stop_sampling()
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "decode":
            if self.output_stdout:
                logging.info("decode stream to stdout")
                with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                    sensor.decode(return_on_stop=not self.stream_wait,
                                  message_timeout_s=self.stream_decode_timeout_s)
            elif self.output_file:
                logging.info(f"decode stream to file {self.output_file}")
                with open(self.output_file, "w") as file:
                    with Py3dpAxxel(self.controller_serial_dev_name) as sensor:
                        sensor.decode(return_on_stop=not self.stream_wait,
                                      message_timeout_s=self.stream_decode_timeout_s, out_file=file)
            else:
                logging.warning("noting to do")
                return 1

        return 0
