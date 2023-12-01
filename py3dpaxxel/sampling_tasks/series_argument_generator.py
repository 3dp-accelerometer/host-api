import uuid
from typing import List, Literal

from py3dpaxxel.storage import filename_stream as fn_generator


class RunArgs:
    """
    Invocation arguments for the one recording step.
    """

    def __init__(self, sequence: int,
                 axis: Literal["x", "y", "z"],
                 frequency_hz: int, zeta_em2: int,
                 file_prefix_1: str,
                 file_prefix_2: str,
                 file_prefix_3: str) -> None:
        self.sequence: int = sequence
        self.axis: Literal["x", "y", "z"] = axis
        self.frequency_hz: int = frequency_hz
        self.zeta_em2: int = zeta_em2
        self.file_prefix_1: str = file_prefix_1
        self.file_prefix_2: str = file_prefix_2
        self.file_prefix_3: str = file_prefix_3

    @property
    def filename(self):
        return fn_generator.generate_filename_for_run(
            self.file_prefix_1,
            self.file_prefix_2,
            self.file_prefix_3,
            self.sequence,
            self.axis,
            self.frequency_hz,
            self.zeta_em2)

    def __str__(self):
        return (f"prefix_1={self.file_prefix_1} "
                f"prefix_2={self.file_prefix_2} "
                f"prefix_3={self.file_prefix_3} "
                f"sequence={self.sequence:03} "
                f"ax={self.axis} "
                f"fx={self.frequency_hz:03} "
                f"zeta={self.zeta_em2:03} "
                f"fn={self.filename}")


class RunArgsGenerator:
    """
    Generates arguments for sequence runner.
    """

    def __init__(self,
                 sequence_repeat_count: int,
                 fx_start_hz: int,
                 fx_stop_hz: int,
                 fx_step_hz: int,
                 zeta_start_em2: int,
                 zeta_stop_em2: int,
                 zeta_step_em2: int,
                 axis: List[Literal["x", "y", "z"]],
                 out_file_prefix_1: str,
                 out_file_prefix_2: str) -> None:
        """

        :param sequence_repeat_count: how often to repeat `Steps`
        :param fx_start_hz: frequency range `*10^0Hz`
        :param fx_stop_hz: frequency range `*10^0Hz`
        :param fx_step_hz: frequency range `*10^0Hz`
        :param zeta_start_em2: Zeta range `*10^-2Zeta`
        :param zeta_stop_em2: Zeta range `*10^-2Zeta`
        :param zeta_step_em2: Zeta range `*10^-2Zeta`
        :param axis: list of x,y,z
        :param out_file_prefix_1: see :class:`py3dpaxxel.cli.filename.generate_filename_for_run`
        :param out_file_prefix_2: see :class:`py3dpaxxel.cli.filename.generate_filename_for_run`
        """
        self.sequence_repeat_count: int = sequence_repeat_count
        self.fx_start_hz: int = fx_start_hz
        self.fx_stop_hz: int = fx_stop_hz
        self.fx_step_hz: int = fx_step_hz
        self.zeta_start_em2: int = zeta_start_em2
        self.zeta_stop_em2: int = zeta_stop_em2
        self.zeta_step_em2: int = zeta_step_em2
        self.axis: List[Literal["x", "y", "z"]] = axis
        self.out_file_prefix_1: str = out_file_prefix_1
        self.out_file_prefix_2: str = out_file_prefix_2

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
            for fx in range(self.fx_start_hz, self.fx_stop_hz + 1, self.fx_step_hz):
                for zeta in range(self.zeta_start_em2, self.zeta_stop_em2 + 1, self.zeta_step_em2):
                    for sequence in range(0, self.sequence_repeat_count):
                        out_file_prefix_3 = f"{uuid.uuid1().time_low:x}"  # each stream shall have a pseudo UUID appended to prefix_2
                        steps.append(RunArgs(sequence, ax, fx, zeta, self.out_file_prefix_1, self.out_file_prefix_2, out_file_prefix_3))
        return steps
