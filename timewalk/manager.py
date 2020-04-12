import sys
from importlib import import_module
import configparser
import logging

from .plugins import internal_plugin_info

logger = logging.getLogger("TimeWalk")

class PluginManager:

    _plugins = {
        "general_plugin": None,
        "adapter": None,
        "formatter": None,
        "lexer": None
    }

    def __init__(self, args, configs):
        self.args = args
        self.configs = configs
        self.plugin_info = internal_plugin_info


    def gather_plugin_info(self):
        plugin_sections = [sect for sect in self.configs.sections() if sect != "Core"]
        for name in plugin_sections:
            mapping = self.configs[name]
            if self._verify_plugin_info(name, mapping):
                self.plugin_info.append(mapping)

    def _verify_plugin_info(self, name, info):
        for key in ("class_name", "role"):
            if key not in info:
                logger.error("Missing '{}' for plugin '{}', please check the config file".format(key, name))
                return False

        if "relative_import_path" not in info and "absolute_package_folder" not in info:
            logger.error("Missing necessary key-val pair for plugin '{}', check the config file".format(name))
            return False

        return True


    # def register(self, classname, mapping):
    #     TODO: implement plugin register function for external plugin (provided absolute path and classname)
        # pass

    # def unregister(self, name):
        # TODO: implement plugin unregister function (delete corresponding section in config file)
        # pass

    # def _change_activation(self, name, value):
        # assert isinstance(value, bool)
        # try:
        #     role = self.configs.get(name, "role")
        #     if role == "general_plugin":
        #         self.configs.set(name, "enabled", str(value))
        # except configparser.NoSectionError:
        #     print("No plugin of name {} is registered. Please check if it is a typo.".format(name))

    # def activate(self, name):
    #     self._change_activation(name, True)
    #
    # def deactivate(self, name):
    #     self._change_activation(name, False)

    def _load_formatter(self):
        class_name = "JSONFormatter" if self.args.command == "query" else "MarkdownReportFormatter"
        for info in self.plugin_info:
            if info["role"] == "formatter" and info["class_name"] == class_name:
                name = info["relative_import_name"]
                cls = info["class_name"]
                try:
                    mod = import_module(name, __package__).__dict__[cls](self.args)
                    return mod
                except ImportError:
                    logger.error("Couldn't find plugin '{}'".format(name))

    def load_plugins(self, role):
        logger.info("Loading {}".format(role))
        plugins = []
        if role == "formatter":
            return self._load_formatter()

        for plugin in [info for info in self.plugin_info if info["role"] == role]:
            if plugin.__contains__("absolute_package_folder"):
                search_path = plugin["absolute_package_folder"]
                sys.path.insert(0, search_path)
                pkg = None
            else:
                pkg = __package__

            name = plugin["relative_import_name"]
            cls = plugin["class_name"]

            try:
                plugins.append(import_module(name, pkg).__dict__[cls](self.args))
            except ImportError:
                logger.error("Couldn't find plugin '{}'".format(name))

            if plugin.__contains__("absolute_package_folder"):
                sys.path.remove(plugin["absolute_package_folder"])

        return plugins if role == "general_plugin" else plugins[0]
