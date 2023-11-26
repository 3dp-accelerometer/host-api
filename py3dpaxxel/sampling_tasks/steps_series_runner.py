import logging
import os
import threading
import time
import uuid
from typing import List, Literal, Tuple, Callable

from py3dpaxxel.controller.constants import OutputDataRate
from py3dpaxxel.octoprint.api import OctoApi
from py3dpaxxel.sampling_tasks.series_argument_generator import RunArgsGenerator, RunArgs
from py3dpaxxel.sampling_tasks.steps_runner import SamplingStepsRunner


class SamplingStepsSeriesRunner(Callable):

    def __init__(self,
                 octoprint_api: OctoApi,
                 controller_serial_device: str,
                 controller_record_timelapse_s: float,
                 controller_decode_timeout_s: float,
                 sensor_odr: OutputDataRate,
                 gcode_start_point_mm: Tuple[int, int, int],
                 gcode_axis: List[Literal["x", "y", "z"]],
                 gcode_distance_mm: int,
                 gcode_step_repeat_count: int,
                 gcode_sequence_repeat_count: int,
                 fx_start_hz: int,
                 fx_stop_hz: int,
                 fx_step_hz: int,
                 zeta_start_em2: int,
                 zeta_stop_em2: int,
                 zeta_step_em2: int,
                 output_file_prefix: str,
                 output_dir: str,
                 do_dry_run: bool,
                 do_abort_flag: threading.Event = threading.Event()) -> None:
        self.octoprint_api: OctoApi = octoprint_api
        self.controller_serial_device: str = controller_serial_device
        self.controller_record_timelapse_s: float = controller_record_timelapse_s
        self.controller_decode_timeout_s: float = controller_decode_timeout_s
        self.sensor_odr: OutputDataRate = sensor_odr
        self.gcode_start_point_mm: Tuple[int, int, int] = gcode_start_point_mm
        self.gcode_axis: List[Literal["x", "y", "z"]] = gcode_axis
        self.gcode_distance_mm: int = gcode_distance_mm
        self.gcode_step_repeat_count: int = gcode_step_repeat_count
        self.gcode_sequence_repeat_count: int = gcode_sequence_repeat_count
        self.fx_start_hz: int = fx_start_hz
        self.fx_stop_hz: int = fx_stop_hz
        self.fx_step_hz: int = fx_step_hz
        self.zeta_start_em2: int = zeta_start_em2
        self.zeta_stop_em2: int = zeta_stop_em2
        self.zeta_step_em2: int = zeta_step_em2
        self.output_file_prefix: str = output_file_prefix
        self.output_dir: str = output_dir
        self.do_dry_run: bool = do_dry_run
        self.do_abort_flag: threading.Event = do_abort_flag

    def __call__(self) -> int:
        generator = RunArgsGenerator(
            sequence_repeat_count=self.gcode_sequence_repeat_count,
            fx_start_hz=self.fx_start_hz,
            fx_stop_hz=self.fx_stop_hz,
            fx_step_hz=self.fx_step_hz,
            zeta_start_em2=self.zeta_start_em2,
            zeta_stop_em2=self.zeta_stop_em2,
            zeta_step_em2=self.zeta_step_em2,
            axis=self.gcode_axis,
            out_file_prefix=self.output_file_prefix,
            out_file_prefix_2=f"{uuid.uuid1().time_low:x}"  # each run shall have a pseudo UUID appended to prefix_1
        )

        runs: List[RunArgs] = generator.generate()
        logging.info(f"planned runs={len(runs)}")

        if 0 == len(runs):
            return 0

        run_count_total = len(runs)
        run_nr = 1
        for r in runs:
            run_percent = int((run_nr / run_count_total) * 100 + 0.5)
            logging.info(f"{run_percent}% run {run_nr}/{run_count_total}")

            start = time.time()
            SamplingStepsRunner(
                input_serial_device=self.controller_serial_device,
                intput_sensor_odr=self.sensor_odr,
                record_timelapse_s=self.controller_record_timelapse_s,
                record_timeout_s=self.controller_decode_timeout_s,
                output_filename=os.path.join(self.output_dir, r.filename),
                octoprint_api=self.octoprint_api,
                gcode_start_point_mm=self.gcode_start_point_mm,
                gcode_extra_gcode=f"M593 {r.axis.upper()} F{r.frequency_hz} D{round((r.zeta_em2/100.0), 2)}",
                gcode_axis=r.axis,
                gcode_distance_mm=self.gcode_distance_mm,
                gcode_step_repeat_count=self.gcode_step_repeat_count,
                gcode_go_start=True if run_nr <= 1 else False,
                gcode_return_start=True,
                gcode_auto_home=True if run_nr <= 1 else False,
                do_dry_run=self.do_dry_run,
                do_abort_flag=self.do_abort_flag)()

            if self.do_abort_flag.is_set():
                logging.warning(f"sequence runner stopped ahead of time after {run_nr} sequences because stop flag was set")
                return -1

            logging.info(f"sampling job done in {time.time() - start:.3f}s")
            time.sleep(0.2)
            run_nr += 1
        return 0
