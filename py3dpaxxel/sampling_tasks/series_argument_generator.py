from typing import List, Literal

from py3dpaxxel.cli import filename as fn_generator


class RunArgs:
    """
    Invocation arguments for the one recording step.
    """

    def __init__(self, step: int, axis: Literal["x", "y", "z"], frequency: int, zeta: int, file_prefix: str) -> None:
        self.step: int = step
        self.axis: Literal["x", "y", "z"] = axis
        self.frequency: int = frequency
        self.zeta: int = zeta
        self.file_prefix: str = file_prefix

    @property
    def filename(self):
        return fn_generator.generate_filename_for_run(self.file_prefix, self.step, self.axis, self.frequency, self.zeta)

    def __str__(self):
        return f"step={self.step:03} ax={self.axis} fx={self.frequency:03} zeta={self.zeta:03} fn={self.filename}"


class RunArgsGenerator:
    """
    Generates arguments for sequence runner.
    """

    def __init__(self,
                 sequence_repeat_count: int,
                 fx_start: int,
                 fx_stop: int,
                 fx_step: int,
                 zeta_start: int,
                 zeta_stop: int,
                 zeta_step: int,
                 axis: List[Literal["x", "y", "z"]],
                 out_file_prefix: str) -> None:
        """

        :param sequence_repeat_count: how often to repeat `Steps`
        :param fx_start: frequency range
        :param fx_stop: frequency range
        :param fx_step: frequency range
        :param zeta_start: Zeta range
        :param zeta_stop: Zeta range
        :param zeta_step: Zeta range
        :param axis: list of x,y,z
        :param out_file_prefix: see :class:`py3dpaxxel.cli.filename.generate_filename_for_run`
        """
        self.sequence_repeat_count: int = sequence_repeat_count
        self.fx_start: int = fx_start
        self.fx_stop: int = fx_stop
        self.fx_step: int = fx_step
        self.zeta_start: int = zeta_start
        self.zeta_stop: int = zeta_stop
        self.zeta_step: int = zeta_step
        self.axis: List[Literal["x", "y", "z"]] = axis
        self.out_file_prefix: str = out_file_prefix

    def generate(self) -> List[RunArgs]:
        """
        Generates a list of arguments for each:

        - axis in axis list for each
        - step in frequency range for each
        - step in Zeta range for each
        - sequence in sequence_repeat_count

        :return: a list of steps within ranges: frequency, zeta, axis and steps
        """
        steps = []
        for ax in self.axis:
            for fx in range(self.fx_start, self.fx_stop + 1, self.fx_step):
                for zeta in range(self.zeta_start, self.zeta_stop + 1, self.zeta_step):
                    for sequence in range(0, self.sequence_repeat_count):
                        steps.append(RunArgs(sequence, ax, fx, zeta, self.out_file_prefix))
        return steps
