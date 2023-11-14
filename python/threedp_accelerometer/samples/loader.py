import csv
import re
from typing import Dict, Union

from threedp_accelerometer.controller.constants import OutputDataRateDelay, OutputDataRate, Range, Scale
from threedp_accelerometer.samples.samples import Samples


class SamplesLoader:
    TABULAR_DELIMITER_CHARACTER = " "
    LINE_COMMENT_CHARACTER = "#"  # comments must start at beginning of line

    def __init__(self, filename: str):
        self.filename = filename

    def _try_read_metadata_if_any(self, samples: Samples):
        # read metadata (if any): ODR, rate, scale
        with open(self.filename, "r") as f:
            for line in reversed(f.readlines()):
                if line[0] == "#":
                    sampling_args = eval(re.search("^# .*({.*})$", line).group(1))
                    samples.rate = OutputDataRate[sampling_args["rate"]]
                    samples.range = Range[sampling_args["range"]]
                    samples.scale = Scale[sampling_args["scale"]]
                    samples.separation_s = OutputDataRateDelay[samples.rate]
                    break

    def load(self):
        samples = Samples()
        self._try_read_metadata_if_any(samples)

        # read samples: requires pre-loaded metadata for timestamp reconstruction
        with open(self.filename, "r") as f:
            reader = csv.DictReader(filter(lambda line: line[0] != self.LINE_COMMENT_CHARACTER, f), delimiter=self.TABULAR_DELIMITER_CHARACTER)
            row: Dict[str, Union[int, float]]
            for row in reader:
                samples.run.append(int(row["run"]))
                index = int(row["sample"])
                samples.index.append(index)
                samples.timestamp_ms.append(index * samples.separation_s * 1000)
                samples.x.append(float(row["x"]))
                samples.y.append(float(row["y"]))
                samples.z.append(float(row["z"]))

        return samples
