import logging
import os, sys, shutil
import time
from testfixtures import LogCapture, OutputCapture
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

class TestArguments(TestCase):

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

    def test_parse_time(self):
        for command in ("query", "report"):
            with self.subTest("test_{}_parse_string_to_int".format(command)):
                start_time = 100000000
                raw_argv = [command, "--start-time", str(start_time), "--end-time", str(start_time + 10)]
                args, _ = parse_arguments(raw_argv)
                self.assertEqual(args.command, command)
                self.assertEqual(args.start_time, start_time)
                self.assertEqual(args.end_time, start_time + 10)

            with self.subTest("test_{}_end_time_smaller_than_start".format(command)):
                raw_argv = [command, "--start-time", str(start_time), "--end-time", str(start_time - 10)]
                with self.assertRaises(ValueError) as cm:
                    args, _ = parse_arguments(raw_argv)
                expected_error_msg = "start_time ({}) should be smaller than end_time ({})".format(
                        start_time, start_time - 10
                    )
                actual_error_msg = cm.exception.args[0]
                self.assertEqual(actual_error_msg, expected_error_msg)

    def test_parse_quoted_filename(self):
        # Note: Don't use single quotes to surround a whitespace-containing filename
        #       It causes error on windows, but works on Linux as using double quotes
        sub_tests = [
            ['"test file name.py"', "test file name.py"],
            ["'no_whitespace.py'", "'no_whitespace.py'"],
            ['''"that's funny"''', "that's funny"],
            ['''"that's what's funnier"''', "that's what's funnier"],
        ]
        for raw_filename, expected_parsed_name in sub_tests:
            with self.subTest(raw_filename):
                raw_argv = ["record", "--file", raw_filename]
                args, _ = parse_arguments(raw_argv)
                self.assertEqual(args.file, expected_parsed_name)

    def test_filename_being_directory(self):
        raw_argv = ["record", "--file", "tests"]
        with self.assertRaises(FileNotFoundError) as cm:
            parse_arguments(raw_argv)
        actual_msg = cm.exception.args[0]
        self.assertTrue(actual_msg.startswith("Input file is a directory"))

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
