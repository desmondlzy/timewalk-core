from .constants import SUCCESS
import sys
import traceback
import logging

logger = logging.getLogger("TimeWalk")


class LifeCycle:

    def __init__(self, timewalk):
        self.ctx = timewalk

    def start(self, command):
        logger.info("Executing command '{}'".format(command))
        if command == "record":
            try:
                self.get_heartbeat()
                self.before_write_heartbeat()  # gather information here
                self.write_heartbeat()
                self.before_write_session()  # combine heartbeats to session here
                self.write_session()

            except Exception as e:
                raise e

        elif command in ("query", "report"):
            try:
                self.query()
                self.before_format()
                self.format()
                self.before_output()
                self.output()

            except Exception as e:
                traceback.print_exc()
                raise e

        logger.info("TimeWalk execution finished!")

        return SUCCESS

    def get_heartbeat(self):
        logger.debug("Phase get_heartbeat")
        self.ctx.heartbeats = self.ctx.adapter.get_heartbeat()
        self.ctx.last_update = self.ctx.heartbeats[-1]["time"] if self.ctx.heartbeats != [] else 0

    def before_write_heartbeat(self):
        logger.debug("Phase before_write_heartbeat")
        self.ctx.current_heartbeat = {
            "time": self.ctx.args.timestamp
        }

        self.ctx.call_plugins("before_write_heartbeat", "gather_heartbeat")

    def write_heartbeat(self):
        logger.debug("Phase write_heartbeat")
        if self.ctx.session_timeout_reached():
            self.ctx.adapter.clear_heartbeat()

        self.ctx.adapter.write_heartbeat(self.ctx.current_heartbeat)

    def before_write_session(self):
        logger.debug("Phase before_write_session")
        if self.ctx.session_timeout_reached():
            self.ctx.current_session = self.ctx.adapter.combine_heartbeat(self.ctx.heartbeats)
            if self.ctx.current_session != {}:
                self.ctx.call_plugins("before_write_session", "merge_heartbeats")

    def write_session(self):
        logger.debug("Phase write_session")
        if self.ctx.session_timeout_reached():
            self.ctx.adapter.write_session(self.ctx.current_session)

    def query(self):
        logger.debug("Phase query")
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
        logger.debug("Phase before_format")
        self.ctx.call_plugins("before_format", "merge_heartbeats")
        self.ctx.call_plugins("before_format", "write_report_section")

    def format(self):
        logger.debug("Phase format")
        content = self.ctx.sessions if self.ctx.args.command == "query" else self.ctx.report_sections
        self.ctx.formatted_data = self.ctx.formatter.format(content)

    def before_output(self):
        logger.debug("Phase before_output")
        self.ctx.call_plugins("before_output", "before_output")

    def output(self):
        logger.debug("Phase output")
        if self.ctx.args.outfile:
            with open(self.ctx.args.outfile, "w") as fp:
                fp.write(self.ctx.formatted_data)
        else:
            sys.stdout.write(self.ctx.formatted_data)
