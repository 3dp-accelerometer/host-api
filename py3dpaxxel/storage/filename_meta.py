import re
from dataclasses import dataclass
from typing import Optional, Literal, Dict, Tuple

from .filename import timestamp_from_args
from .filename_fft import generate_filename_for_fft_regex, generate_filename_for_fft
from .filename_stream import generate_filename_for_run_regex, generate_filename_for_run


@dataclass
class FilenameMeta:
    """
    Helper for parsing metadata from file name.
    """

    prefix: Optional[str] = None
    prefix_2: Optional[str] = None
    prefix_3: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    second: Optional[int] = None
    milli_second: Optional[int] = None
    sequence_nr: Optional[int] = None
    sequence_axis: Optional[Literal["x", "y", "z"]] = None
    sequence_frequency_hz: Optional[int] = None
    sequence_zeta_em2: Optional[int] = None

    def from_filename_meta(self, from_obj: "FilenameMeta") -> "FilenameMeta":
        for k, v in vars(from_obj).items():
            self.__setattr__(k, v)
        return self

    @staticmethod
    def regex_group_mapping(has_prefix_1: bool = True,
                            has_prefix_2: bool = True,
                            has_prefix_3: bool = True) -> Dict[int, Tuple[str, type]]:
        if has_prefix_3 and has_prefix_2 and has_prefix_1:
            return {
                1: ("prefix_1", str),
                2: ("prefix_2", str),
                3: ("prefix_3", str),
                4: ("year", int),
                5: ("month", int),
                6: ("day", int),
                7: ("hour", int),
                8: ("minute", int),
                9: ("second", int),
                10: ("milli_second", int),
                11: ("sequence_nr", int),
                12: ("sequence_axis", str),
                13: ("sequence_frequency_hz", int),
                14: ("sequence_zeta_em2", int),
            }
        elif has_prefix_2 and has_prefix_1:
            return {
                1: ("prefix_1", str),
                2: ("prefix_2", str),
                3: ("year", int),
                4: ("month", int),
                5: ("day", int),
                6: ("hour", int),
                7: ("minute", int),
                8: ("second", int),
                9: ("milli_second", int),
                10: ("sequence_nr", int),
                11: ("sequence_axis", str),
                12: ("sequence_frequency_hz", int),
                13: ("sequence_zeta_em2", int),
            }
        elif has_prefix_1:
            return {
                1: ("prefix_1", str),
                2: ("year", int),
                3: ("month", int),
                4: ("day", int),
                5: ("hour", int),
                6: ("minute", int),
                7: ("second", int),
                8: ("milli_second", int),
                9: ("sequence_nr", int),
                10: ("sequence_axis", str),
                11: ("sequence_frequency_hz", int),
                12: ("sequence_zeta_em2", int),
            }
        else:  # no prefix
            return {
                1: ("year", int),
                2: ("month", int),
                3: ("day", int),
                4: ("hour", int),
                5: ("minute", int),
                6: ("second", int),
                7: ("milli_second", int),
                8: ("sequence_nr", int),
                9: ("sequence_axis", str),
                10: ("sequence_frequency_hz", int),
                11: ("sequence_zeta_em2", int),
            }

    def read_attr_from_meta(self, filename: str, regex: str, re_group_mapping: Dict[int, Tuple[str, type]]):
        regexp = re.compile(regex)
        match = regexp.match(filename)

        assert len(match.groups()) == len(re_group_mapping.items())

        for group_index, (attr, type_cast) in re_group_mapping.items():
            setattr(self, attr, type_cast(match.group(group_index)))

        return self


@dataclass
class FilenameMetaStream(FilenameMeta):
    """
    Helper for parsing metadata from stream file name.
    """

    file_extension: Optional[str] = None

    def from_filename(self,
                      filename: str,
                      has_prefix_1: bool = True,
                      has_prefix_2: bool = True,
                      has_prefix_3: bool = True) -> "FilenameMetaStream":
        """
        Matches file name pattern and interprets data contained in name.

        :param filename: input string, i.e. "axxel-0815-20231110-182030456-s100-ax-f200-z300.tsv"
        :param has_prefix_1: whether prefix 1 is contained ("axxel")
        :param has_prefix_2: whether prefix 2 is contained too ("0815")
        :param has_prefix_3: whether prefix 2 is contained too ("")
        :return: self
        """

        re_group_mapping: Dict[int, Tuple[str, type]] = self.regex_group_mapping(has_prefix_1=has_prefix_1,
                                                                                 has_prefix_2=has_prefix_2,
                                                                                 has_prefix_3=has_prefix_3)
        last_index = max(re_group_mapping.keys())
        re_group_mapping[last_index + 1] = ("file_extension", str)
        regex_str = generate_filename_for_run_regex(with_prefix_1=has_prefix_1,
                                                    with_prefix_2=has_prefix_2,
                                                    with_prefix_3=has_prefix_3)

        return self.read_attr_from_meta(filename, regex_str, re_group_mapping)

    def from_filename_meta_fft(self, from_obj: "FilenameMetaFft") -> "FilenameMetaStream":
        self.from_filename_meta(from_obj)
        self.__delattr__("fft_axis")
        return self

    def to_filename(self, with_current_timestamp: bool = True) -> str:
        return generate_filename_for_run(
            prefix_1=self.prefix_1,
            prefix_2=self.prefix_2,
            prefix_3=self.prefix_3,
            sequence_nr=self.sequence_nr,
            axis=self.sequence_axis,
            frequency=self.sequence_frequency_hz,
            zeta=self.sequence_zeta_em2,
            ext=self.file_extension,
            force_timestamp=None if with_current_timestamp else timestamp_from_args(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.milli_second))


@dataclass
class FilenameMetaFft(FilenameMeta):
    """
    Helper for parsing metadata from FFT file name.
    """

    fft_axis: Optional[str] = None
    file_extension: Optional[str] = None

    def from_filename(self,
                      filename: str,
                      has_prefix_1: bool = True,
                      has_prefix_2: bool = True,
                      has_prefix_3: bool = True) -> "FilenameMetaFft":
        """
        Matches file name pattern and interprets data contained in name.

        :param filename: input string, i.e. "fft-0815-20231110-182030456-s100-ax-f200-z300-z.tsv"
        :param has_prefix_1: whether prefix 1 is contained ("fft")
        :param has_prefix_2: whether prefix 2 is contained too ("0815")
        :param has_prefix_3: whether prefix 2 is contained too ("")
        :return: self
        """

        if has_prefix_2 and has_prefix_1:
            re_group_mapping: Dict[int, Tuple[str, type]] = self.regex_group_mapping(has_prefix_1=has_prefix_1,
                                                                                     has_prefix_2=has_prefix_2,
                                                                                     has_prefix_3=has_prefix_3)
            last_index = max(re_group_mapping.keys())
            re_group_mapping[last_index + 1] = ("fft_axis", str)
            re_group_mapping[last_index + 2] = ("file_extension", str)
            regex_str = generate_filename_for_fft_regex(with_prefix_1=has_prefix_1,
                                                        with_prefix_2=has_prefix_2,
                                                        with_prefix_3=has_prefix_3)

            return self.read_attr_from_meta(filename, regex_str, re_group_mapping)

    def from_filename_meta_stream(self, from_obj: FilenameMetaStream) -> "FilenameMetaFft":
        self.from_filename_meta(from_obj)
        return self

    def to_filename(self, with_current_timestamp: bool = True) -> str:
        return generate_filename_for_fft(
            prefix_1=self.prefix_1,
            prefix_2=self.prefix_2,
            prefix_3=self.prefix_3,
            sequence_nr=self.sequence_nr,
            axis=self.sequence_axis,
            frequency=self.sequence_frequency_hz,
            zeta=self.sequence_zeta_em2,
            fft_axis=self.fft_axis,
            ext=self.file_extension,
            force_timestamp=None if with_current_timestamp else timestamp_from_args(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.milli_second))
