import logging
import threading
import time
from typing import Literal, Tuple, Optional

from py3dpaxxel.controller.background_decoder import BackgroundDecoder
from py3dpaxxel.controller.constants import OutputDataRate
from py3dpaxxel.gcode.trajectory_generator import CoplanarTrajectory
from py3dpaxxel.octoprint.api import OctoApi


class SamplingStepsRunner:
    def __init__(self,
                 input_serial_device: str,
                 intput_sensor_odr: OutputDataRate,
                 record_timelapse_s: float,
                 output_filename: Optional[str],
                 octoprint_api: OctoApi,
                 gcode_start_point_mm: Tuple[int, int, int],
                 gcode_extra_gcode: Optional[str],
                 gcode_axis: Literal["x", "y", "z"],
                 gcode_distance_mm: int,
                 gcode_repetitions: int,
                 gcode_go_start: bool,
                 gcode_return_start: bool,
                 gcode_auto_home: bool,
                 do_dry_run: bool,
                 ) -> None:
        self.input_serial_device: str = input_serial_device
        self.intput_sensor_odr: OutputDataRate = intput_sensor_odr
        self.record_timelapse_s: float = record_timelapse_s
        self.output_filename: Optional[str] = output_filename
        self.octoprint_api: OctoApi = octoprint_api
        self.gcode_start_point_mm: Tuple[int, int, int] = gcode_start_point_mm
        self.gcode_extra_gcode: Optional[str] = gcode_extra_gcode
        self.gcode_axis: Literal["x", "y", "z"] = gcode_axis
        self.gcode_distance_mm: int = gcode_distance_mm
        self.gcode_repetitions: int = gcode_repetitions
        self.gcode_go_start: bool = gcode_go_start
        self.gcode_return_start: bool = gcode_return_start
        self.gcode_auto_home: bool = gcode_auto_home
        self.do_dry_run: bool = do_dry_run

    def run(self) -> int:
        decoder = BackgroundDecoder(self.input_serial_device,
                                    self.record_timelapse_s,
                                    self.intput_sensor_odr,
                                    self.output_filename,
                                    self.do_dry_run)
        controller_task = threading.Thread(target=decoder)
        controller_task.start()

        time.sleep(0.1)
        start = time.time()
        decoder.start_sampling()

        commands = [self.gcode_extra_gcode] if "" != self.gcode_extra_gcode else []
        commands.extend(CoplanarTrajectory.generate(
            axis=self.gcode_axis,
            start_xyz_mm=self.gcode_start_point_mm,
            distance_mm=self.gcode_distance_mm,
            repetitions=self.gcode_repetitions,
            go_to_start=self.gcode_go_start,
            return_to_start=self.gcode_return_start,
            auto_home=self.gcode_auto_home))
        self.octoprint_api.send_commands(commands)

        logging.info("waiting for decoding task finished...")
        controller_task.join()
        logging.info(f"sampling task done in {time.time() - start:.3f}s")
        logging.info("waiting for decoding task finished... done")

        return 0
