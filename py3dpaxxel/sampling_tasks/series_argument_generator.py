from typing import List, Literal

from py3dpaxxel.cli import filename as fn_generator


class RunArgs:
    def __init__(self, run: int, axis: Literal["x", "y"], frequency: int, zeta: int, file_prefix: str) -> None:
        self.run: int = run
        self.axis: Literal["x", "y"] = axis
        self.frequency: int = frequency
        self.zeta: int = zeta
        self.file_prefix: str = file_prefix

    @property
    def filename(self):
        return fn_generator.generate_filename_for_run(self.file_prefix, self.run, self.axis, self.frequency, self.zeta)

    def __str__(self):
        return f"run={self.run:03} ax={self.axis} fx={self.frequency:03} zeta={self.zeta:03} fn={self.filename}"


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
                 file_prefix: str) -> None:
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
                        runs.append(RunArgs(run, ax, fx, zeta, self.file_prefix))
        return runs
