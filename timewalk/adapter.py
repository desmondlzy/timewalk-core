import logging
import sqlite3
import json

logger = logging.getLogger("TimeWalk")


class SqliteAdapter():
    version = "0.0.1"

    def __init__(self, args):
        self.args = args
        self.timestamp = args.timestamp
        self.conn = sqlite3.connect(args.database)
        self.conn.row_factory = sqlite3.Row
        self._init_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        self.conn.close()

    def _init_database(self):
        sql_init_tables = """
        CREATE TABLE IF NOT EXISTS heartbeat (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER NOT NULL,
            json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS session (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            start INTEGER NOT NULL,
            end   INTEGER NOT NULL,
            json  TEXT NOT NULL
        );
        """
        self.conn.executescript(sql_init_tables)

    def get_heartbeat(self, start=None, end=None):
        if start == None:
            start = 0
        if end == None:
            end = float("inf")

        with self.conn:
            cur = self.conn.cursor()
            sql = "SELECT json FROM heartbeat WHERE time >= ? AND time <= ? ORDER BY time ASC"
            cur.execute(sql, (start, end))
            heartbeats = [json.loads(row["json"]) for row in cur.fetchall()]

        return heartbeats

    def write_heartbeat(self, data):
        if not data.__contains__("time"):
            data["time"] = self.timestamp

        with self.conn:
            cur = self.conn.cursor()
            sql = "INSERT INTO heartbeat (time, json) VALUES (?, ?)"
            cur.execute(sql, (data["time"], json.dumps(data)))

        return cur.lastrowid

    def clear_heartbeat(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.executescript("DELETE FROM heartbeat")

    def get_session(self, start=None, end=None, include_current=False):
        if start == None:
            start = 0
        if end == None:
            end = float("inf")

        with self.conn:
            cur = self.conn.cursor()
            sql = "SELECT json FROM session WHERE end >= ? AND start <= ? ORDER BY start ASC"
            cur.execute(sql, (start, end))
            sessions = [json.loads(row["json"]) for row in cur.fetchall()]

        if include_current:
            heartbeats = self.get_heartbeat(start, end)
            cur_sess = self.combine_heartbeat(heartbeats)
            if cur_sess is not None and len(cur_sess) > 1:
                sessions.append(cur_sess)

        return sessions

    def write_session(self, session):
        if session == {}:
            return

        assert session.__contains__("start")
        assert session.__contains__("end")
        with self.conn:
            cur = self.conn.cursor()
            sql = "INSERT INTO session (start, end, json) VALUES (?, ?, ?)"
            cur.execute(sql, (session["start"], session["end"], json.dumps(session)))

        return cur.lastrowid

    def combine_heartbeat(self, heartbeats):
        # filter and sort heartbeat records chronologically
        heartbeats.sort(key=lambda rec: rec["time"])

        session = {}
        if len(heartbeats) > 1:
            session["start"] = heartbeats[0]["time"]
            session["end"] = heartbeats[-1]["time"]
            session["duration"] = session["end"] - session["start"]

        return session
