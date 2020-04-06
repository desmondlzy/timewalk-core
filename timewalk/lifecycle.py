from .constants import SUCCESS
import sys
import traceback
import logging

logger = logging.getLogger("TimeWalk")


class LifeCycle:

    def __init__(self, timewalk):
        self.ctx = timewalk

    def start(self, command):
        if command == "record":
            try:
                self.get_heartbeat()
                self.before_write_heartbeat()  # gather information here
                self.write_heartbeat()
                self.before_write_session()  # combine heartbeats to session here
                self.write_session()
                return SUCCESS

            except Exception as e:
                raise e

        elif command in ("query", "report"):
            try:
                self.query()
                self.before_format()
                self.format()
                self.before_output()
                self.output()
                return SUCCESS

            except Exception as e:
                traceback.print_exc()
                raise e

    def get_heartbeat(self):
        self.ctx.heartbeats = self.ctx.adapter.get_heartbeat()
        self.ctx.last_update = self.ctx.heartbeats[-1]["time"] if self.ctx.heartbeats != [] else 0

    def before_write_heartbeat(self):
        self.ctx.current_heartbeat = {
            "time": self.ctx.args.timestamp
        }

        self.ctx.call_plugins("before_write_heartbeat", "gather_heartbeat")

    def write_heartbeat(self):
        if self.ctx.args.timestamp - self.ctx.last_update > 60:
            self.ctx.adapter.clear_heartbeat()

        self.ctx.adapter.write_heartbeat(self.ctx.current_heartbeat)

    def before_write_session(self):
        if self.ctx.args.timestamp - self.ctx.last_update > 60:
            self.ctx.current_session = self.ctx.adapter.combine_heartbeat(self.ctx.heartbeats)
            self.ctx.call_plugins("before_write_session", "merge_heartbeats")

    def write_session(self):
        if self.ctx.args.timestamp - self.ctx.last_update > 60:
            self.ctx.adapter.write_session(self.ctx.current_session)

    def query(self):
        self.ctx.heartbeats = self.ctx.adapter.get_heartbeat(
            self.ctx.args.start_time,
            self.ctx.args.end_time,
        )
        self.ctx.current_session = self.ctx.adapter.combine_heartbeat(self.ctx.heartbeats)
        self.ctx.sessions = self.ctx.adapter.get_session(
            self.ctx.args.start_time,
            self.ctx.args.end_time,
            include_current=False
        )
        if self.ctx.current_session:
            self.ctx.sessions.append(self.ctx.current_session)

        self.ctx.report_sections = []

    # gather information from sessions and heartbeats
    def before_format(self):
        self.ctx.call_plugins("before_format", "merge_heartbeats")
        self.ctx.call_plugins("before_format", "write_report_section")

    def format(self):
        content = self.ctx.sessions if self.ctx.args.command == "query" else self.ctx.report_sections
        self.ctx.formatted_data = self.ctx.formatter.format(content)

    def before_output(self):
        self.ctx.call_plugins("before_output", "before_output")

    def output(self):
        if self.ctx.args.outfile:
            with open(self.ctx.args.outfile, "w") as fp:
                fp.write(self.ctx.formatted_data)
        else:
            sys.stdout.write(self.ctx.formatted_data)
