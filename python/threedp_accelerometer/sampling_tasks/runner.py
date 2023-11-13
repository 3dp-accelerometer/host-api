from typing import List, Literal

from threedp_accelerometer.sampling_tasks.series_argument_generator import RunArgsGenerator


class SamplingSeriesRunner:

    def __init__(self,
                 runs: int,
                 fx_start: int,
                 fx_stop: int,
                 fx_step: int,
                 zeta_start: int,
                 zeta_stop: int,
                 zeta_step: int,
                 axis: List[Literal["x", "y"]],
                 file_prefix: str):
        self.runs: int = runs
        self.fx_start: int = fx_start
        self.fx_stop: int = fx_stop
        self.fx_step: int = fx_step
        self.zeta_start: int = zeta_start
        self.zeta_stop: int = zeta_stop
        self.zeta_step: int = zeta_step
        self.axis: List[Literal["x", "y"]] = axis
        self.file_prefix: str = file_prefix

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
            file_prefix=self.file_prefix)

        runs = generator.generate()

        print(f"computed runs={len(runs)}")
        for r in runs:
            print(str(r))

        return 0
