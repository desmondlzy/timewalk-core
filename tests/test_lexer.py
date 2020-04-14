from datetime import timedelta, datetime
from .utils import TestCase, MockedNamespace, TestingDB

from timewalk.lexer import TimeWalkLexer

class TestLexer(TestCase):

    def test_guess_by_input_name(self):
        args = MockedNamespace({
            "language": "PYTHON",
            "file": "tests/samples/codefiles/python.py"
        })

        twl = TimeWalkLexer(args)
        actual_lang = twl.get_language()
        self.assertEqual(actual_lang, "Python")

