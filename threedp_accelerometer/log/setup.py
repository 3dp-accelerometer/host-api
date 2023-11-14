import logging.config

import yaml


def configure_logging():
    with open('logging.yaml', 'rt') as f:
        cfg = yaml.safe_load(f.read())
        logging.config.dictConfig(cfg)
