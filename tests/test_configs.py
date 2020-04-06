import unittest
import os
import logging
from testfixtures import LogCapture

from .utils import TestCase, MockedNamespace
from timewalk.logger import setup_logging
from timewalk.manager import PluginManager
from timewalk.configs import parse_configs

from timewalk.configs import parse_configs, save_configs


class MyTestCase(TestCase):
    def test_parse_configs_normally(self):
        settings = [
            {
                "file": "empty.ini",
                "expected_sections": set()
            },
            {
                "file": "many_plugins.ini",
                "expected_sections": {"Core", "PluginA", "PluginB", "UsefulPlugin", "UselessPlugin"}
            }
        ]

        for setting in settings:
            configs = parse_configs(os.path.join(os.getcwd(), "tests/samples/configs", setting["file"]))
            sections = configs.sections()
            self.assertEqual(set(sections), setting["expected_sections"])

    def test_parse_configs_file_not_found(self):
        file = "brilliant_test_case.ini"
        if os.path.exists(file):
            os.remove(file)

        configs = parse_configs(file)
        sections = configs.sections()
        self.assertEqual(set(sections), set())

        if os.path.exists(file):
            os.remove(file)
