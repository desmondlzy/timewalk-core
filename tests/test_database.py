from datetime import datetime

from .utils import TestCase, MockedNamespace, TestingDB
from testfixtures import TempDirectory

from timewalk.adapter import SqliteAdapter


class TestDatabase(TestCase):

    def setUp(self):
        self.timestamp = int(datetime(2019, 12, 26, 23, 59, 59).timestamp())

    def tearDown(self):
        try:
            TempDirectory.cleanup_all()
        except:
            pass

    def test_empty_database_get(self):
        with TestingDB("empty.db") as db:
            args = MockedNamespace({
                "timestamp": self.timestamp,
                "database": db.path,
            })

            with SqliteAdapter(args) as adapter:
                result = adapter.get_session()
                expected = []
                self.assertEqual(result, expected)
                result = adapter.get_heartbeat()
                expected = []
                self.assertEqual(result, expected)

    def test_empty_database_heartbeat(self):
        with TestingDB("empty.db") as db:
            args = MockedNamespace({
                "database": db.path,
                "timestamp": self.timestamp
            })

            with SqliteAdapter(args) as adapter:
                end_delta = 10 * 60
                for delta in range(0, end_delta + 1, 60):
                    data = {
                        "language": "python",
                        "time": self.timestamp + delta
                    }
                    doc_id = adapter.write_heartbeat(data)
                    self.assertTrue(doc_id >= 0)

                with self.subTest(name="fullTimeRange"):
                    actual_heartbeats = adapter.get_heartbeat()
                    self.assertEqual(len(actual_heartbeats), 11)
                    self.assertListEqual(actual_heartbeats, sorted(actual_heartbeats, key=lambda hb: hb["time"]),
                                         "heartbeats must be sorted chronologically")
                    actual_session = adapter.get_session()
                    self.assertEqual(len(actual_session), 0,
                                     "By default, current session will not be included")
                    actual_session = adapter.get_session(include_current=True)
                    self.assertEqual(len(actual_session), 1)
                    self.assertEqual(actual_session[0]["duration"], end_delta)
                    self.assertEqual(actual_session[0]["start"], self.timestamp)
                    self.assertEqual(actual_session[0]["end"], self.timestamp + end_delta)

                with self.subTest(name="earlyEnd"):
                    actual_heartbeats = adapter.get_heartbeat(end=self.timestamp + 5 * 60)
                    self.assertEqual(len(actual_heartbeats), 6)
                    self.assertListEqual(actual_heartbeats, sorted(actual_heartbeats, key=lambda hb: hb["time"]),
                                         "heartbeats must be sorted chronologically")
                    actual_session = adapter.get_session(end=self.timestamp + 5 * 60, include_current=True)
                    self.assertEqual(len(actual_session), 1)
                    self.assertEqual(actual_session[0]["duration"], 5 * 60)
                    self.assertEqual(actual_session[0]["start"], self.timestamp)
                    self.assertEqual(actual_session[0]["end"], self.timestamp + 5 * 60)

                with self.subTest(name="lateStart"):
                    actual_heartbeats = adapter.get_heartbeat(start=self.timestamp + 2 * 60)
                    self.assertEqual(len(actual_heartbeats), 9,
                                     "should get {} heartbeats but actually {}".format(9, len(actual_heartbeats)))
                    self.assertListEqual(actual_heartbeats, sorted(actual_heartbeats, key=lambda hb: hb["time"]),
                                         "heartbeats must be sorted chronologically")
                    actual_session = adapter.get_session(start=self.timestamp + 2 * 60)
                    self.assertEqual(len(actual_session), 0)

                    actual_session = adapter.get_session(start=self.timestamp + 2 * 60, include_current=True)
                    self.assertEqual(len(actual_session), 1)
                    self.assertEqual(actual_session[0]["duration"], end_delta - 2 * 60)
                    self.assertEqual(actual_session[0]["start"], self.timestamp + 2 * 60)
                    self.assertEqual(actual_session[0]["end"], self.timestamp + end_delta)

                with self.subTest(name="inMiddle"):
                    kwargs = {
                        "start": self.timestamp + 2 * 60 + 3.5,
                        "end": self.timestamp + 5 * 60 - 2.5
                    }
                    actual_heartbeats = adapter.get_heartbeat(**kwargs)
                    self.assertEqual(len(actual_heartbeats), 2,
                                     "should get {} heartbeats but actually {}".format(9, len(actual_heartbeats)))
                    self.assertListEqual(actual_heartbeats, sorted(actual_heartbeats, key=lambda hb: hb["time"]),
                                         "heartbeats must be sorted chronologically")
                    actual_session = adapter.get_session(**kwargs, include_current=True)
                    self.assertEqual(len(actual_session), 1)
                    self.assertEqual(actual_session[0]["duration"], 1 * 60)
                    self.assertEqual(actual_session[0]["start"], self.timestamp + 3 * 60)
                    self.assertEqual(actual_session[0]["end"], self.timestamp + 4 * 60)

    def test_empty_database_session(self):
        with TestingDB("empty.db") as db:
            args = MockedNamespace({
                "database": db.path,
                "timestamp": self.timestamp
            })

            with SqliteAdapter(args) as adapter:
                end_delta = 10 * 60
                for delta in range(0, end_delta + 1, 60):
                    data = {
                        "language": "python",
                        "time": self.timestamp + delta
                    }
                    doc_id = adapter.write_heartbeat(data)
                    self.assertTrue(doc_id >= 0)

                session_num = 200
                duration = 2 * 60 * 60
                interval = 1 * 60 * 60

                for i in range(1, session_num + 1):
                    sess_start = self.timestamp - i * (duration + interval)
                    sess_end = self.timestamp - i * (duration + interval) + duration

                    session = {
                        "start": sess_start,
                        "end": sess_end,
                        "duration": duration,
                        "language": {
                            "c": duration // 3,
                            "cpp": duration // 2,
                            "go": duration // 6
                        }
                    }

                    adapter.write_session(session)

                settings = [
                    {
                        "name": "fullTimeRange, heartbeatExcluded",
                        "kwargs": {"include_current": False},
                        "expected_num": 200,
                        "expected_first_start": self.timestamp - session_num * (duration + interval),
                        "expected_last_end": self.timestamp - 1 * (duration + interval) + duration
                    },
                    {
                        "name": "earlyStop",
                        "kwargs": {"end": self.timestamp - 1 * (duration + interval) + duration - 60},
                        "expected_num": 200,
                        "expected_first_start": self.timestamp - session_num * (duration + interval),
                        "expected_last_end": self.timestamp - 1 * (duration + interval) + duration
                    },
                    {
                        "name": "lateStart, heartbeatExcluded",
                        "kwargs": {
                            "start": self.timestamp - 100 * (duration + interval) - 20,
                            "include_current": False
                        },
                        "expected_num": 100,
                        "expected_first_start": self.timestamp - 100 * (duration + interval),
                        "expected_last_end": self.timestamp - 1 * (duration + interval) + duration
                    },
                    {
                        "name": "emptyQuery",
                        "kwargs": {
                            "start": self.timestamp + 2000
                        },
                        "expected_num": 0,
                    }
                ]

                for st in settings:
                    actual_sessions = adapter.get_session(**st["kwargs"])
                    with self.subTest(name=st["name"]):
                        self.assertEqual(len(actual_sessions), st["expected_num"],
                                         "in '{}', actual_session_num {} != expected_num {}".format(
                                             st["name"], len(actual_sessions), st["expected_num"]))
                        self.assertListEqual(actual_sessions, sorted(actual_sessions, key=lambda s: s["start"]),
                                             "sessions should be sorted by 'start' chorologically")
                        if st["name"] != "emptyQuery":
                            self.assertEqual(actual_sessions[0]["start"], st["expected_first_start"],
                                             "in '{}' actual and expected 'start' of first session doesn't agree ({} != {})".format(
                                                 st["name"], actual_sessions[0]["start"], st["expected_first_start"]
                                             ))
                            self.assertEqual(actual_sessions[-1]["end"], st["expected_last_end"],
                                             "in '{}' actual and expected 'end' of last session doesn't agree ({} != {})".format(
                                                 st["name"], actual_sessions[0]["end"], st["expected_last_end"]
                                             ))

    def test_clear_heartbeat(self):
        with TestingDB("empty.db") as db:
            args = MockedNamespace({
                "database": db.path,
                "timestamp": self.timestamp
            })

            with SqliteAdapter(args) as adapter:
                end_delta = 10 * 60
                for delta in range(0, end_delta + 1, 60):
                    data = {
                        "language": "python",
                        "time": self.timestamp + delta
                    }
                    doc_id = adapter.write_heartbeat(data)
                    self.assertTrue(doc_id >= 0)

                sess = {
                    "start": self.timestamp - 2000,
                    "end": self.timestamp - 1000,
                    "duration": 1000
                }
                adapter.write_session(sess)

                adapter.clear_heartbeat()

                actual_heartbeats = adapter.get_heartbeat()
                actual_sessions = adapter.get_session()
                self.assertListEqual(actual_heartbeats, [])
                self.assertListEqual(actual_sessions, [sess])
