import csv
from typing import Dict

from lib.device_constants import OutputDataRateDelay, OutputDataRate


class Samples:
    def __init__(self, output_data_rate: OutputDataRate):
        self.separation_ms = OutputDataRateDelay[output_data_rate] * 1000
        self.run = []
        self.index = []
        self.timestamp_ms = []
        self.x = []
        self.y = []
        self.z = []

    def __len__(self):
        return len(self.index)


class SamplesLoader:
    TABULAR_DELIMITER_CHARACTER = " "
    LINE_COMMENT_CHARACTER = "#"  # comments must start at beginning of line

    def __init__(self, file_name: str):
        self.file_name = file_name

    def load(self):
        samples = Samples(OutputDataRate.ODR3200)

        with open(self.file_name, "r") as f:
            reader = csv.DictReader(filter(lambda line: line[0] != self.LINE_COMMENT_CHARACTER, f), delimiter=self.TABULAR_DELIMITER_CHARACTER)
            row: Dict[str, int | float]
            for row in reader:
                samples.run.append(int(row["run"]))
                index = int(row["sample"])
                samples.index.append(index)
                samples.timestamp_ms.append(index * samples.separation_ms)
                samples.x.append(float(row["x"]))
                samples.y.append(float(row["y"]))
                samples.z.append(float(row["z"]))

        return samples
