import logging.config
import os

import yaml


def configure_logging() -> None:
    """
    Convenience function to set up logging from logging.yaml file.

    :return: None
    """
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logging.yaml"), "rt") as f:
        cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(cfg)
