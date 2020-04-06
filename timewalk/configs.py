import traceback
import os
import configparser
import logging

logger = logging.getLogger("TimeWalk")


def parse_configs(file, encoding="utf-8"):
    assert file is not None

    if not os.path.exists(file):
        logger.info("No config file found in {}, creating an empty config file at default location".format(file))

        # create an empty file in the location
        with open(file, "w", encoding=encoding):
            pass

    if os.path.exists(file):
        with open(file, "r", encoding=encoding) as f:
            try:
                configs = configparser.ConfigParser()
                configs.read_file(f)
                return configs
            except configparser.Error:
                logger.error(traceback.format_exc())
                raise SystemExit(404)


def save_configs(file, config, encoding="utf-8"):
    with open(file, "w", encoding=encoding) as f:
        try:
            config.write(f)
        except configparser.Error:
            logger.error(traceback.format_exc())
            raise SystemExit(404)
