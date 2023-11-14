import logging
from typing import Union

from serial.tools.list_ports import comports

from .api import Adxl345
from .constants import OutputDataRate, Range, Scale


class ControllerRunner:

    def __init__(self,
                 command: Union[str, None],
                 controller_serial_dev_name: Union[str, None],
                 controller_do_list_devices: Union[bool, None],
                 controller_do_reboot: Union[bool, None],
                 sensor_output_data_rate: Union[OutputDataRate, None],
                 sensor_scale: Union[Scale, None],
                 sensor_range: Union[Range, None],
                 sensor_all_settings: Union[bool, None],
                 stream_start: Union[int, None],
                 stream_stop: Union[bool, None],
                 stream_decode: Union[bool, None],
                 output_file: Union[str, None],
                 output_stdout: Union[bool, None],
                 ):
        self.command: Union[str, None] = command
        self.controller_serial_dev_name: Union[str, None] = controller_serial_dev_name
        self.controller_do_list_devices: Union[bool, None] = controller_do_list_devices
        self.controller_do_reboot: Union[bool, None] = controller_do_reboot
        self.sensor_output_data_rate: Union[OutputDataRate, None] = sensor_output_data_rate
        self.sensor_scale: Union[Scale, None] = sensor_scale
        self.sensor_range: Union[Range, None] = sensor_range
        self.sensor_all_settings: Union[bool, None] = sensor_all_settings
        self.stream_start: Union[int, None] = stream_start
        self.stream_stop: Union[bool, None] = stream_stop
        self.stream_decode: Union[bool, None] = stream_decode
        self.output_file: Union[str, None] = output_file
        self.output_stdout: Union[bool, None] = output_stdout

    def run(self) -> int:
        if not self.command:
            return -1

        if self.command == "device":
            if self.controller_do_list_devices:
                for s in comports():
                    logging.info("%s %s %s %s", s.device, s.manufacturer, s.description, s.hwid)
            elif self.controller_do_reboot:
                logging.info("device reboot")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.reboot()
            else:
                logging.warning("noting to do")

        elif self.command == "set":
            if self.sensor_output_data_rate:
                logging.info("send outputdatarate=%s", self.sensor_output_data_rate.name)
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.set_output_data_rate(self.sensor_output_data_rate)
            elif self.sensor_scale:
                logging.info("send scale=%s", self.sensor_scale.name)
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.set_scale(self.sensor_scale)
            elif self.sensor_range:
                logging.info("send range=%s", self.sensor_range.name)
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.set_range(self.sensor_range)
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "get":
            if self.sensor_output_data_rate:
                logging.debug("request odr")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
            elif self.sensor_scale:
                logging.debug("request scale")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    logging.info("scale=%s", sensor.get_scale().name)
            elif self.sensor_range:
                logging.debug("request range")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    logging.info("range=%s", sensor.get_range().name)
            elif self.sensor_all_settings:
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    logging.info("odr=%s", sensor.get_output_data_rate().name)
                    logging.info("scale=%s", sensor.get_scale().name)
                    logging.info("range=%s", sensor.get_range().name)
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "stream":
            if self.stream_start is not None:
                logging.info("sampling start n=%s", self.stream_start)
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.start_sampling(self.stream_start)
            elif self.stream_stop:
                logging.info("sampling stop")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.stop_sampling()
            elif self.stream_decode:
                logging.info("sampling decode")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.decode()
            else:
                logging.warning("noting to do")
                return 1

        elif self.command == "decode":
            if self.output_stdout:
                logging.info("decode stream to stdout")
                with Adxl345(self.controller_serial_dev_name) as sensor:
                    sensor.decode(return_on_stop=False)
            if self.output_file:
                logging.info(f"decode stream to file {self.output_file}")
                with open(self.output_file, "w") as file:
                    with Adxl345(self.controller_serial_dev_name) as sensor:
                        sensor.decode(return_on_stop=True, file=file)
            else:
                logging.warning("noting to do")
                return 1

        return 0
