import os
import re
from dataclasses import dataclass, field
from typing import List


@dataclass(init=False)
class File:
    full_path: str
    _full_path: str = field(init=False, repr=False)
    filename_ext: str
    filename_no_ext: str
    directory: str
    extension: str

    def __init__(self, full_path: str = "file-does-not.exist") -> None:
        self.full_path = full_path

    @property
    def full_path(self) -> str:
        return self._full_path

    @full_path.setter
    def full_path(self, full_path: str):
        self._full_path = full_path
        self.filename_ext = os.path.basename(full_path)
        self.filename_no_ext = os.path.splitext(self.filename_ext)[0]
        self.directory = os.path.dirname(full_path)
        self.extension = os.path.splitext(self.filename_ext)[1]


class FileSelector:
    def __init__(self, file_name_regexp: str) -> None:
        self.directory = os.path.join(".", os.path.dirname(file_name_regexp))
        self.filename = os.path.basename(file_name_regexp)

    def filter(self) -> List[File]:
        regex = re.compile(self.filename)

        files = []
        for file in [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]:
            if regex.match(file):
                files.append(File(os.path.join(self.directory, file)))

        return files
