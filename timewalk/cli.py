# -*- coding: utf-8 -*-
"""
    timewalk.cli
    ~~~~~~~~~~~~

    Command-line entry point of TimeWalk.

    This code file is heavily borrowed from wakatime.cli
    https://github.com/wakatime/wakatime/blob/master/wakatime/cli.py

"""

import os
import sys



# get path to local timewalk package and update the env variable
package_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, package_folder)

try:
    import timewalk
except (TypeError, ImportError):
    # on Windows, non-ASCII characters in import path can be fixed using
    # the script path from sys.argv[0].
    # More info at https://github.com/wakatime/wakatime/issues/32
    package_folder = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    sys.path.insert(0, package_folder)
    import timewalk


if __name__ == '__main__':
    sys.exit(timewalk.execute(sys.argv[1:]))
