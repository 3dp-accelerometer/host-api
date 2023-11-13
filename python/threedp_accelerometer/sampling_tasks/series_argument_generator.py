from typing import List, Literal

from threedp_accelerometer.cli import file_name as fn_generator


class RunArgs:
    def __init__(self, run: int, frequency: int, zeta: float, file_name: str):
        self.run: int = run
        self.frequency: int = frequency
        self.zeta: float = zeta
        self.filename: str = file_name

    def __str__(self):
        return f"run={self.run:03} fx={self.frequency:03} zeta={self.zeta:03} fn={self.filename}"


class RunArgsGenerator:

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

    def generate(self) -> List[RunArgs]:
        runs = []
        for ax in self.axis:
            for fx in range(self.fx_start, self.fx_stop + 1, self.fx_step):
                for run in range(0, self.runs):
                    for zeta in range(self.zeta_start, self.zeta_stop + 1, self.zeta_step):
                        runs.append(RunArgs(run, fx, zeta,
                                            fn_generator.generate_filename_for_run(self.file_prefix, run, ax, fx, zeta)))
        return runs
