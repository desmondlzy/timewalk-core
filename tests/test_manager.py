import unittest
import os
import logging
from testfixtures import LogCapture

from .utils import TestCase, MockedNamespace
from timewalk.logger import setup_logging
from timewalk.manager import PluginManager
from timewalk.configs import parse_configs
import configparser

class TestManager(TestCase):
    def setUp(self):
        logging.disable(logging.NOTSET)

    def test_load_plugins(self):
        args = MockedNamespace({
            "database": os.path.join(os.getcwd(), "tests/samples/databases/empty.db"),
            "file": os.path.join(os.getcwd(), "tests/samples/codefiles/python.py"),
            "timestamp": int(10 ** 9)
        })
        configs = parse_configs("tests/samples/configs/empty.ini")
        manager = PluginManager(args, configs)

        roles = (
            "general_plugin",
            "adapter",
            "lexer",
            "formatter"
        )
        for role in roles:
            with self.subTest(name=role):
                plugins = manager.load_plugins(role)
                if role == "general_plugin":
                    self.assertEqual(type(plugins), type([]))

    def test_missing_classname(self):
        args = MockedNamespace({})
        configs = configparser.ConfigParser()
        configs.read_dict({
            "Core": {},
            "test": {
                "role": "general_plugin",
                "enabled": "true",
                "absolute_package_folder": os.path.join(os.getcwd(), "tests/samples/plugins"),
                "relative_import_name": "test_plugin"
            }
        })
        manager = PluginManager(args, configs)
        with LogCapture() as l:
            manager.gather_plugin_info()
            l.check(
                ("TimeWalk", "ERROR", "Missing 'class_name' for plugin 'test', please check the config file")
            )

    def test_missing_role(self):
        args = MockedNamespace({})
        configs = configparser.ConfigParser()
        configs.read_dict({
            "Core": {},
            "test": {
                "enabled": "true",
                "class_name": "TestPlugin",
                "absolute_package_folder": os.path.join(os.getcwd(), "tests/samples/plugins"),
                "relative_import_name": "test_plugin"
            }
        })
        manager = PluginManager(args, configs)
        with LogCapture() as l:
            manager.gather_plugin_info()
            l.check(
                ("TimeWalk", "ERROR", "Missing 'role' for plugin 'test', please check the config file")
            )

    def test_missing_absolute_path_external_plugin(self):
        args = MockedNamespace({})
        configs = configparser.ConfigParser()
        configs.read_dict({
            "Core": {},
            "test": {
                "role": "general_plugin",
                "enabled": "true",
                "class_name": "TestPlugin",
                "relative_import_name": "test_plugin"
            }
        })
        manager = PluginManager(args, configs)
        with LogCapture() as l:
            manager.gather_plugin_info()
            l.check(
                ("TimeWalk", "ERROR", "Missing necessary key-val pair for plugin 'test', check the config file")
            )

    def test_get_plugin_info_normally(self):
        args = MockedNamespace({})
        configs = configparser.ConfigParser()
        configs.read_dict({
            "Core": {},
            "test": {
                "enabled": "true",
                "role": "general_plugin",
                "class_name": "TestPlugin",
                "absolute_package_folder": os.path.join(os.getcwd(), "tests/samples/plugins"),
                "relative_import_name": "test_plugin"
            }
        })
        manager = PluginManager(args, configs)
        with LogCapture() as l:
            manager.gather_plugin_info()
            l.check()

if __name__ == '__main__':
    unittest.main()
