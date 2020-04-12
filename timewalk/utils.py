import logging
import os
from .constants import *

log = logging.getLogger('TimeWalk')


def get_user_home():
    return os.path.expanduser('~')


def get_timewalk_home():
    home = os.environ.get('TIMEWALK_HOME')
    if home:
        base = os.path.expanduser(home)
    else:
        base = os.path.join(get_user_home(), DIRNAME_HOME)
        if not os.path.exists(base):
            os.makedirs(base)

    return base


def get_default_database():
    return os.path.join(get_timewalk_home(), FILENAME_DATABASE)


def get_default_log():
    return os.path.join(get_timewalk_home(), FILENAME_LOG)


def get_default_config():
    return os.path.join(get_timewalk_home(), FILENAME_CONFIG)

