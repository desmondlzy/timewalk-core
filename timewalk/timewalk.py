import logging

from timewalk.manager import PluginManager
from .utils import get_user_home, get_timewalk_home

logger = logging.getLogger("TimeWalk")

class TimeWalk:

    _tokens = None
    _session_timeout = 150
    last_update = None

    def __init__(self, args, configs):
        self.args = args
        self._manager = PluginManager(args, configs)
        self.adapter = self._manager.load_plugins("adapter")
        self.logger = logging.getLogger("TimeWalk")

        if args.command == "record":
            self.lexer = self._manager.load_plugins("lexer")
        elif args.command in ("query", "report"):
            self.formatter = self._manager.load_plugins("formatter")

        self.plugins = self._manager.load_plugins("general_plugin")

        logger.info("TimeWalk initialized")

    def call_plugins(self, event, handler_name):
        self.current_event = event
        for plugin in self.plugins:
            if hasattr(plugin, handler_name):
                try:
                    logger.debug("Calling plugin {}:{} for event {}".format(plugin, handler_name, event))
                    getattr(plugin, handler_name)(self)
                except Exception as e:
                    logger.warning("Plugin '{}' yields an error from '{}' when handling '{}': {}".format(
                        plugin.name, handler_name, event, e))

    def session_timeout_reached(self):
        assert self.last_update is not None
        return self.args.timestamp - self.last_update > self.session_timeout

    @property
    def session_timeout(self):
        return self._session_timeout

    @session_timeout.setter
    def session_timeout(self, val):
        raise ValueError("heartbeat_interval is read-only")

    def get_user_home(self):
        return get_user_home()

    def get_timewalk_home(self):
        return get_timewalk_home()
