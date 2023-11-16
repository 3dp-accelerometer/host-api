import logging
import os
import time
from typing import List, Literal, Tuple

from py3dpaxxel.controller.constants import OutputDataRate
from py3dpaxxel.octoprint.runner import SamplingJobRunner
from py3dpaxxel.sampling_tasks.series_argument_generator import RunArgsGenerator, RunArgs


class SamplingSeriesRunner:

    def __init__(self,
                 octoprint_address: str,
                 octoprint_port: int,
                 octoprint_key: str,
                 controller_serial_device: str,
                 controller_record_timelapse_s: float,
                 sensor_odr: OutputDataRate,
                 gcode_start_point_mm: Tuple[int, int, int],
                 gcode_axis: List[Literal["x", "y", "z"]],
                 gcode_distance_mm: int,
                 gcode_repetitions: int,
                 runs: int,
                 fx_start: int,
                 fx_stop: int,
                 fx_step: int,
                 zeta_start: int,
                 zeta_stop: int,
                 zeta_step: int,
                 axis: List[Literal["x", "y", "z"]],
                 output_file_prefix: str,
                 output_dir: str,
                 do_dry_run: bool) -> None:
        self.octoprint_address: str = octoprint_address
        self.octoprint_port: int = octoprint_port
        self.octoprint_key: str = octoprint_key
        self.controller_serial_device: str = controller_serial_device
        self.controller_record_timelapse_s: float = controller_record_timelapse_s
        self.sensor_odr: OutputDataRate = sensor_odr
        self.gcode_start_point_mm: Tuple[int, int, int] = gcode_start_point_mm
        self.gcode_axis: List[Literal["x", "y", "z"]] = gcode_axis
        self.gcode_distance_mm: int = gcode_distance_mm
        self.gcode_repetitions: int = gcode_repetitions
        self.runs: int = runs
        self.fx_start: int = fx_start
        self.fx_stop: int = fx_stop
        self.fx_step: int = fx_step
        self.zeta_start: int = zeta_start
        self.zeta_stop: int = zeta_stop
        self.zeta_step: int = zeta_step
        self.axis: List[Literal["x", "y", "z"]] = axis
        self.output_file_prefix: str = output_file_prefix
        self.output_dir: str = output_dir
        self.do_dry_run: bool = do_dry_run

    def run(self) -> int:
        generator = RunArgsGenerator(
            runs=self.runs,
            fx_start=self.fx_start,
            fx_stop=self.fx_stop,
            fx_step=self.fx_step,
            zeta_start=self.zeta_start,
            zeta_stop=self.zeta_stop,
            zeta_step=self.zeta_step,
            axis=self.axis,
            file_prefix=self.output_file_prefix)

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
            job_runner = SamplingJobRunner(
                input_serial_device=self.controller_serial_device,
                intput_sensor_odr=self.sensor_odr,
                record_timelapse_s=self.controller_record_timelapse_s,
                output_filename=os.path.join(self.output_dir, r.filename),
                octoprint_address=self.octoprint_address,
                octoprint_port=self.octoprint_port,
                octoprint_api_key=self.octoprint_key,
                gcode_start_point_mm=self.gcode_start_point_mm,
                gcode_extra_gcode=f"M593 {r.axis.upper()} F{r.frequency} D{r.zeta}",
                gcode_axis=r.axis,
                gcode_distance_mm=self.gcode_distance_mm,
                gcode_repetitions=self.gcode_repetitions,
                gcode_go_start=True if run_nr <= 1 else False,
                gcode_return_start=True,
                gcode_auto_home=True if run_nr <= 1 else False,
                do_dry_run=self.do_dry_run)
            job_runner.run()
            logging.info(f"sampling job done in {time.time() - start:.3f}s")
            time.sleep(0.2)
            run_nr += 1
        return 0
