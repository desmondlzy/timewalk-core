import logging
import os, sys, shutil
import time
from testfixtures import LogCapture, OutputCapture
import unittest

from .utils import TestCase

from timewalk.utils import *
from timewalk.arguments import parse_arguments
from timewalk.constants import *
from timewalk.main import execute

arguments = {
    "command",
    "timestamp",
    "file",
    "config",
    "log_file",
    "database",
}

class ArgumentsTestCase(TestCase):

    def test_program_help(self):
        argv = ["--help"]
        with OutputCapture() as o:
            execute(argv)
        with open("tests/samples/output/test_program_help.txt", "r") as f:
            self.assertEqual(o.captured, f.read())

    def test_command_help(self):
        argv = ["record", "--help"]
        with OutputCapture() as o:
            execute(argv)
        with open("tests/samples/output/test_command_help.txt", "r") as f:
            self.assertEqual(o.captured, f.read())

    def test_parse_record_command(self):
        raw_argv = [
            "record",
            "--database", "./database.db",
            "--file", "./python.py",
        ]
        args, _ = parse_arguments(raw_argv)
        self.assertEqual(args.command, "record")
        self.assertEqual(args.file, os.path.join("./python.py"))
        self.assertEqual(args.database, os.path.join("./database.db"))
        self.assertEqual(args.log_file, os.path.join(get_timewalk_home(), FILENAME_LOG))
        self.assertEqual(args.config, os.path.join(get_timewalk_home(), FILENAME_CONFIG))
        self.assertEqual(args.language, None)
        self.assertIsInstance(args.timestamp, int)

    def test_default_values(self):
        raw_argv = [
            "record",
            "--file", "./python.py",
        ]
        args, _ = parse_arguments(raw_argv)
        self.assertEqual(args.command, "record")
        self.assertEqual(args.file, os.path.join("./python.py"))
        self.assertEqual(args.database, get_default_database())
        self.assertEqual(args.log_file, get_default_log())
        self.assertEqual(args.config, get_default_config())
        self.assertEqual(args.language, None)
        self.assertIsInstance(args.timestamp, int)

    # TODO: make this testcase work
    # def test_missing_command(self):
    #     unittest.skip("")
    #     raw_argv = [
    #         "--database", "./database.db",
    #         "--file", "./python.py",
    #     ]
    #     try:
    #         args, _ = parse_arguments(raw_argv)
    #     except Exception:
    #         pass
