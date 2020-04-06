import logging
import os
import traceback
import json

from collections import OrderedDict


class JsonFormatter(logging.Formatter):

    def setup(self, timestamp, version, verbose, warnings=False):
        self.timestamp = timestamp
        self.version = version
        self.verbose = verbose
        self.warnings = warnings

    def format(self, record, *args):
        data = OrderedDict([
            ('now', self.formatTime(record, self.datefmt)),
        ])
        data['version'] = self.version
        data['time'] = self.timestamp
        if self.verbose:
            pass
        data['level'] = record.levelname
        data['message'] = record.getMessage() if self.warnings else record.msg
        return json.dumps(data)

    def traceback(self, lvl=None):
        logger = logging.getLogger('TimeWalk')
        if not lvl:
            lvl = logger.getEffectiveLevel()
        logger.log(lvl, traceback.format_exc())


def set_log_level(logger, verbose):
    level = logging.WARN
    if verbose:
        level = logging.DEBUG
    logger.setLevel(level)


def setup_logging(args, version):
    logger = logging.getLogger('TimeWalk')
    for handler in logger.handlers:
        logger.removeHandler(handler)
    set_log_level(logger, args.verbose)
    log_file = args.log_file
    handler = logging.FileHandler(os.path.expanduser(log_file))
    formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
    formatter.setup(
        timestamp=args.timestamp,
        version=version,
        verbose=args.verbose,
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # add custom traceback logging method
    logger.traceback = formatter.traceback

    warnings_formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
    warnings_formatter.setup(
        timestamp=args.timestamp,
        version=version,
        verbose=args.verbose,
        warnings=True,
    )
    warnings_handler = logging.FileHandler(os.path.expanduser(log_file))
    warnings_handler.setFormatter(warnings_formatter)
    logging.getLogger('py.warnings').addHandler(warnings_handler)
    logging.captureWarnings(True)

    return logger
