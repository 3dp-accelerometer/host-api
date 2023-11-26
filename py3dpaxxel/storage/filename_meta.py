import re
from typing import Optional, Literal, Dict, Tuple

from py3dpaxxel.storage.filename import generate_filename_for_run_regex


class FilenameMeta:
    def __init__(self):
        self.prefix_1: Optional[str] = None
        self.prefix_2: Optional[str] = None
        self.year: Optional[int] = None
        self.month: Optional[int] = None
        self.day: Optional[int] = None
        self.hour: Optional[int] = None
        self.minute: Optional[int] = None
        self.second: Optional[int] = None
        self.milli_second: Optional[int] = None
        self.sequence_nr: Optional[int] = None
        self.sequence_axis: Optional[Literal["x", "y", "z"]] = None
        self.sequence_frequency_hz: Optional[int] = None
        self.sequence_zeta_em2: Optional[int] = None
        self.file_extension: Optional[str] = None

    def from_filename(self, filename: str, has_prefix_1: bool = True, has_prefix_2: bool = True) -> "FilenameMeta":
        """
        Matches file name pattern and interprets data contained in name.

        :param filename: input string, i.e. "foo-bar-20231110-182030456-s100-ax-f200-z300.tsv"
        :param has_prefix_1: whether prefix 1 is contained ("foo")
        :param has_prefix_2: whether prefix 2 is contained too ("bar")
        :return: self
        """

        if has_prefix_2 and has_prefix_1:
            re_group_mapping: Dict[str, Tuple[int, type]] = {
                "prefix_1": (1, str),
                "prefix_2": (2, str),
                "year": (3, int),
                "month": (4, int),
                "day": (5, int),
                "hour": (6, int),
                "minute": (7, int),
                "second": (8, int),
                "milli_second": (9, int),
                "sequence_nr": (10, int),
                "sequence_axis": (11, str),
                "sequence_frequency_hz": (12, int),
                "sequence_zeta_em2": (13, int),
                "file_extension": (14, str),
            }
        elif has_prefix_1:
            re_group_mapping: Dict[str, Tuple[int, type]] = {
                "prefix_1": (1, str),
                "year": (2, int),
                "month": (3, int),
                "day": (4, int),
                "hour": (5, int),
                "minute": (6, int),
                "second": (7, int),
                "milli_second": (8, int),
                "sequence_nr": (9, int),
                "sequence_axis": (10, str),
                "sequence_frequency_hz": (11, int),
                "sequence_zeta_em2": (12, int),
                "file_extension": (13, str),
            }
        else:
            re_group_mapping: Dict[str, Tuple[int, type]] = {
                "year": (1, int),
                "month": (2, int),
                "day": (3, int),
                "hour": (4, int),
                "minute": (5, int),
                "second": (6, int),
                "milli_second": (7, int),
                "sequence_nr": (8, int),
                "sequence_axis": (9, str),
                "sequence_frequency_hz": (10, int),
                "sequence_zeta_em2": (11, int),
                "file_extension": (12, str),
            }

        regexp = re.compile(generate_filename_for_run_regex(with_prefix_1=has_prefix_1, with_prefix_2=has_prefix_2))
        match = regexp.match(filename)
        assert len(match.groups()) == len(re_group_mapping.items())

        for attr, (group_index, type_cast) in re_group_mapping.items():
            setattr(self, attr, type_cast(match.group(group_index)))

        return self
