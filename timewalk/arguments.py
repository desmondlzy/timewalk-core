import os, sys
import re
from time import time
import datetime
import argparse

from .__about__ import __version__
from .configs import parse_configs
from .constants import *
from .utils import *


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str) and values.startswith('"'):
            values = re.sub(r'\\"', '"', values.strip('"'))
        if os.path.isdir(values):
            raise FileNotFoundError("Input file is a directory: '{}'".format(values))
        try:
            if os.path.isfile(values):
                values = os.path.realpath(values)
        except:
            pass
        setattr(namespace, self.dest, values)


class StoreWithoutQuotes(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str) and values.startswith('"'):
            values = re.sub(r'\\"', '"', values.strip('"'))
        setattr(namespace, self.dest, values)

class ParseTimestamp(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, int(values))

class TopParser(argparse.ArgumentParser):
    def print_usage(self, file=None):
        prog_usage = "usage: timewalk <command> [options]"
        print(prog_usage)

    def print_help(self, file=None):
        self.print_usage()
        prog_epilog = \
""" 
There are some useful timewalk commands:

    record          Generate one heartbeat and record coding activity
    query           Query for the coding stats in json over some time range 
    report          Generate a human readable report over a time range

Use `timewalk <command> --help' to see help for a specific command"""
        print(prog_epilog)


def parse_arguments(raw_argv):
    """Parse command line arguments and configs from ~/.timewalk/timewalk.cfg.
    Command line arguments take precedence over config file settings.
    Returns instances of ArgumentParser and SafeConfigParser.
    """

    # define supported command line arguments
    parser = TopParser(prog='timewalk')

    parser.add_argument('--version', action='version', version=__version__)

    subparsers = parser.add_subparsers(dest="command", parser_class=argparse.ArgumentParser)
    parser_record = subparsers.add_parser("record")
    parser_query = subparsers.add_parser('query')
    parser_report = subparsers.add_parser('report')

    # set up shared arguments
    for psr in (parser_record, parser_query, parser_report):
        psr.add_argument('--config', dest='config', action=StoreWithoutQuotes,
                            metavar='FILE', help='Defaults to ~/.timewalk/config.ini')
        psr.add_argument('--database', dest='database', action=StoreWithoutQuotes,
                            metavar='FILE', help='Defaults to ~/.timewalk/{}'.format(FILENAME_DATABASE))
        psr.add_argument('--log-file', dest='log_file',
                            metavar='FILE', action=StoreWithoutQuotes,
                            help='Defaults to ~/.timewalk/timewalk.log.')
        psr.add_argument('--verbose', dest='verbose', action='store_true',
                            help='Turns on debug messages in log file.')
        psr.add_argument('--invoker', dest='invoker', action=StoreWithoutQuotes,
                                   help='The editor plugin that invokes the core program and its version')


    parser_record.add_argument('--file', dest='file', action=FileAction,
                        help=argparse.SUPPRESS, required=True)
    parser_record.add_argument('--write', dest='is_write', action='store_true',
                        help='When set, triggered from writing to a file.')
    parser_record.add_argument('--project', dest='project', action=StoreWithoutQuotes,
                     help='Optional project name.')
    parser_record.add_argument('--language', dest='language',
                     action=StoreWithoutQuotes,
                     help='Optional language name. If valid, takes ' +
                          'priority over auto-detected language.')

    parser_query.add_argument('--start-time', dest='start_time', metavar="time", action=ParseTimestamp,
                      help='Start time for query. Unix timestamp, default to the time of' +
                           'the first record')
    parser_query.add_argument('--end-time', dest='end_time', metavar="time",
                      help='End time for query. In ISO format (YYYY-MM-DD) or Unix timestamp, default to present time',
                        action=ParseTimestamp)
    parser_query.add_argument('--outfile', dest="outfile", metavar="FILE", action=FileAction,
                      help='Output statistics to specified file instead of standard output, if the file is not empty, overwrite')

    parser_report.add_argument('--format', dest='format', choices=['markdown'], default='markdown',
                              help='Format of the report, choose from "markdown" (for human)')
    parser_report.add_argument('--start-time', dest='start_time', metavar="time", action=ParseTimestamp,
                              help='Start time for query. Unix timestamp, default to the time of' +
                                   '7 days before --end-time')
    parser_report.add_argument('--end-time', dest='end_time', metavar="time",
                              help='End time for query. Unix timestamp, default to present time',
                              action=ParseTimestamp)
    parser_report.add_argument('--outfile', dest="outfile", metavar="FILE", action=FileAction,
                              help='Output statistics to specified file instead of standard output, if the file is not empty, overwrite')
    # parse command line arguments
    args = parser.parse_args(raw_argv)

    home = get_timewalk_home()
    if not os.path.exists(home):
        os.makedirs(home)

    # parse ~/config.ini file
    if not args.config:
        args.config = os.path.join(home, FILENAME_CONFIG)

    configs = parse_configs(args.config)

    if not args.log_file and configs.has_option('Core', 'log_file'):
        args.log_file = configs.get('Core', 'log_file')
    if not args.log_file:
        args.log_file = os.path.join(home, FILENAME_LOG)

    if not args.database:
        args.database = get_default_database()

    # use current unix epoch timestamp by default
    if not hasattr(args, 'timestamp'):
        setattr(args, 'timestamp', int(time()))
    if not args.timestamp:
        args.timestamp = int(time())

    if args.command == "record":
        if not args.verbose and configs.has_option('Core', 'verbose'):
            args.verbose = configs.getboolean('Core', 'verbose')
        if not args.verbose and configs.has_option('Core', 'debug'):
            args.verbose = configs.getboolean('Core', 'debug')

    elif args.command == "query":
        if not args.start_time:
            args.start_time = 0
        if not args.end_time:
            args.end_time = args.timestamp

        if args.start_time > args.end_time:
            raise ValueError("start_time ({}) should be smaller than end_time ({})".format(
                args.start_time, args.end_time
            ))

    elif args.command == "report":
        if not args.end_time:
            args.end_time = args.timestamp
        if not args.start_time:
            args.start_time = args.end_time - datetime.timedelta(days=7).total_seconds()

        if args.start_time > args.end_time:
            raise ValueError("start_time ({}) should be smaller than end_time ({})".format(
                args.start_time, args.end_time
            ))

    elif args.command == "plugin":
        # TODO: plugin related command
        pass

    return args, configs

