import unittest
import os, sys
import json
from datetime import datetime, timezone, timedelta
from testfixtures import Replace, test_time, OutputCapture, LogCapture
from .utils import TempDirectory, TestingDB

import logging

from timewalk import execute
from timewalk.constants import SUCCESS


class TestIntegration(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.NOTSET)
        self.timestamp = int(datetime(2019, 12, 26, 23, 59, 59).timestamp())

    def tearDown(self):
        try:
            TempDirectory.cleanup_all()
        except Exception:
            pass

    def test_version_info(self):
        about = {}
        with open("./timewalk/__about__.py") as f:
            exec(f.read(), about)
        expected_version = about["__version__"]

        raw_argv = ["--version"]
        with OutputCapture() as o:
            execute(raw_argv)
        o.compare(expected_version)

    def test_initialization(self):
        with TestingDB("empty.db") as db:
            argv = [
                "record",
                "--file", os.path.join("tests", "samples", "codefiles", "python.py"),
                "--database", db.path,
                "--config", "tests/samples/configs/empty.ini"
            ]

            retval = execute(argv)
            self.assertEqual(SUCCESS, retval)

    def test_query(self):
        with TestingDB("empty.db") as db, Replace(
                "timewalk.arguments.time", test_time(delta=50, delta_type="seconds")):
            start_time = datetime(2001, 1, 1)
            codefiles = ("python.py", "go.go", "swift.swift")
            for file in codefiles:
                argv = [
                    "record",
                    "--file", os.path.join("tests", "samples", "codefiles", file),
                    "--database", db.path,
                    "--config", "tests/samples/configs/empty.ini"
                ]
                retval = execute(argv)

            argv = [
                "query",
                "--database", db.path,
            ]

            with OutputCapture() as o, LogCapture() as l:
                retval = execute(argv)
                output_text = o.captured
                l.check()
            try:
                actual = json.loads(output_text)
            except json.JSONDecodeError as e:
                print(o.captured)
                raise e
            expected = [
                {
                    "start": int(start_time.replace(tzinfo=timezone.utc).timestamp()),
                    "end": int(start_time.replace(tzinfo=timezone.utc).timestamp()) + 50 * (len(codefiles) - 1),
                    "duration": (50 * (len(codefiles) - 1)),
                    "invoker": {},
                    "project": {},
                    "language": {"Go": 50, "Swift": 50},
                },
            ]
            self.assertListEqual(expected, actual)

    def test_query_output_to_file(self):
        with TestingDB("empty.db") as db:
            start_time = datetime(2001, 1, 1)
            with Replace("timewalk.arguments.time", test_time(delta=50, delta_type="seconds")):
                codefiles = ("python.py", "go.go", "swift.swift")
                projects = ("Plugin", None, "Plugin")
                for file, proj in zip(codefiles, projects):
                    argv = [
                        "record",
                        "--file", os.path.join("tests", "samples", "codefiles", file),
                        "--database", db.path,
                        "--config", "tests/samples/configs/empty.ini"
                    ]
                    if proj:
                        argv += ["--project", proj]
                    retval = execute(argv)

                output_file_name = "./test_query_output_to_file.txt"
                argv = [
                    "query",
                    "--database", db.path,
                    "--outfile", output_file_name
                ]

                retval = execute(argv)
                try:
                    with open(output_file_name) as f:
                        actual = json.load(f)
                except json.JSONDecodeError as e:
                    raise e
                expected = [
                    {
                        "start": int(start_time.replace(tzinfo=timezone.utc).timestamp()),
                        "end": int(start_time.replace(tzinfo=timezone.utc).timestamp()) + 50 * (len(codefiles) - 1),
                        "duration": (50 * (len(codefiles) - 1)),
                        "invoker": {},
                        "project": {"Plugin": 50},
                        "language": {"Go": 50, "Swift": 50},
                    },
                ]
                self.assertListEqual(expected, actual)

                if os.path.exists(output_file_name):
                    os.remove(output_file_name)

    def test_report(self):
        with TestingDB("empty.db") as db, Replace(
                "timewalk.arguments.time", test_time(None)) as d:
            codefiles = ("python.py", "go.go", "swift.swift")

            seconds = [0, 20, 50]
            for file, t in zip(codefiles, seconds):
                start_date = datetime(2001, 1, 1, 0, 0, t, 0)
                d.set(start_date)
                argv = [
                    "record",
                    "--file", os.path.join("tests", "samples", "codefiles", file),
                    "--database", db.path,
                    "--project", "My Plugin",
                    "--invoker", '"testAgent/1.0.0-alpha timewalk-testAgent/0.5.0"',
                    "--config", "tests/samples/configs/empty.ini"
                ]
                retval = execute(argv)

            start_date = datetime(2001, 1, 1, 0, 0, 55, 0)
            d.set(start_date)
            argv = [
                "report",
                "--database", db.path,
            ]

            with OutputCapture() as o, LogCapture() as l:
                retval = execute(argv)
                output_text = o.captured

            with open("./tests/samples/output/test_report.txt", "r") as f:
                sevendays = timedelta(days=7)
                expected_start = datetime.fromtimestamp(
                    (start_date - sevendays).replace(tzinfo=timezone.utc).timestamp()).strftime("%b %d, %Y %H:%M:%S")
                expected_end = datetime.fromtimestamp(
                    start_date.replace(tzinfo=timezone.utc).timestamp()).strftime("%b %d, %Y %H:%M:%S")
                expected = f.read().format(expected_start, expected_end)
                self.assertEqual(output_text, expected)

    def test_large_report(self):
        with TestingDB("empty.db") as db, Replace(
                "timewalk.arguments.time", test_time(None)) as d:
            codefiles = ("python.py", "go.go", "swift.swift")
