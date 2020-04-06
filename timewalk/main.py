import logging
import os
import sys
import traceback

pwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(pwd))
sys.path.insert(0, os.path.join(pwd, 'packages'))

from .__about__ import __version__
from .arguments import parse_arguments
from .logger import setup_logging

log = logging.getLogger('TimeWalk')

from .timewalk import TimeWalk
from .lifecycle import LifeCycle


def execute(argv=None):

    if argv:
        sys.argv = ['timewalk'] + argv

    try:
        args, configs = parse_arguments(sys.argv[1:])
    except SystemExit as ex:
        return ex.code

    setup_logging(args, __version__)

    tw = TimeWalk(args, configs)

    try:
        lifecycle = LifeCycle(tw)
        return_val = lifecycle.start(args.command)
        return return_val
    except Exception:
        log.error(logging.ERROR, exc_info=True)
        print(traceback.format_exc())
        return -1
