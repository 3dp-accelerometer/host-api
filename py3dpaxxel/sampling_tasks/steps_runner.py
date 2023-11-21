import logging
import threading
import time
from typing import Literal, Tuple, Optional, Callable

from py3dpaxxel.controller.blocking_decoder import BlockingDecoder
from py3dpaxxel.controller.constants import OutputDataRate
from py3dpaxxel.gcode.trajectory_generator import CoplanarTrajectory
from py3dpaxxel.log.setup import configure_logging
from py3dpaxxel.octoprint.api import OctoApi
from py3dpaxxel.sampling_tasks.exception_task_wrapper import ExceptionTaskWrapper

configure_logging()


class SamplingStepsRunner(Callable):
    def __init__(self,
                 input_serial_device: str,
                 intput_sensor_odr: OutputDataRate,
                 record_timelapse_s: float,
                 record_timeout_s: float,
                 output_filename: Optional[str],
                 octoprint_api: OctoApi,
                 gcode_start_point_mm: Tuple[int, int, int],
                 gcode_extra_gcode: Optional[str],
                 gcode_axis: Literal["x", "y", "z"],
                 gcode_distance_mm: int,
                 gcode_step_repeat_count: int,
                 gcode_go_start: bool,
                 gcode_return_start: bool,
                 gcode_auto_home: bool,
                 do_dry_run: bool,
                 do_abort_flag: threading.Event = threading.Event()) -> None:
        self.input_serial_device: str = input_serial_device
        self.intput_sensor_odr: OutputDataRate = intput_sensor_odr
        self.record_timelapse_s: float = record_timelapse_s
        self.output_filename: Optional[str] = output_filename
        self.octoprint_api: OctoApi = octoprint_api
        self.gcode_start_point_mm: Tuple[int, int, int] = gcode_start_point_mm
        self.gcode_extra_gcode: Optional[str] = gcode_extra_gcode
        self.gcode_axis: Literal["x", "y", "z"] = gcode_axis
        self.gcode_distance_mm: int = gcode_distance_mm
        self.gcode_step_repeat_count: int = gcode_step_repeat_count
        self.gcode_go_start: bool = gcode_go_start
        self.gcode_return_start: bool = gcode_return_start
        self.gcode_auto_home: bool = gcode_auto_home
        self.do_dry_run: bool = do_dry_run
        self.record_timeout_s: float = record_timeout_s
        self.do_abort_flag: threading.Event = do_abort_flag

    def __call__(self) -> int:
        blocking_decoder = BlockingDecoder(
            self.input_serial_device,
            self.record_timelapse_s,
            self.record_timeout_s,
            self.intput_sensor_odr,
            self.output_filename,
            self.do_dry_run,
            self.do_abort_flag)
        exception_wrapper = ExceptionTaskWrapper(target=blocking_decoder)
        decoder_thread = threading.Thread(name="stream_decoder", target=exception_wrapper)
        decoder_thread.daemon = True

        decoder_thread.start()

        time.sleep(0.1)
        start = time.time()
        blocking_decoder.start_sampling()

        commands = [self.gcode_extra_gcode] if "" != self.gcode_extra_gcode else []
        commands.extend(CoplanarTrajectory.generate(
            axis=self.gcode_axis,
            start_xyz_mm=self.gcode_start_point_mm,
            distance_mm=self.gcode_distance_mm,
            step_repeat_count=self.gcode_step_repeat_count,
            go_to_start=self.gcode_go_start,
            return_to_start=self.gcode_return_start,
            auto_home=self.gcode_auto_home))

        self.octoprint_api.send_commands(commands)

        logging.debug("waiting for decoding task finished...")
        decoder_thread.join()

        exceptions_count = len(exception_wrapper.exceptions)
        if 0 < exceptions_count:
            logging.error(f"subprocess terminated with {exceptions_count} exceptions, will raise first")
            raise exception_wrapper.exceptions[0]

        logging.debug(f"decoding task done in {time.time() - start:.3f}s")

        return 0
