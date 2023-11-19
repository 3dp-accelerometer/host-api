import logging.config
import os

import yaml


def configure_logging():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logging.yaml"), "rt") as f:
        cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(cfg)
