import logging
import os, shutil
import sys
import tempfile
import unittest
from testfixtures import TempDirectory


class TestCase(unittest.TestCase):
    pass


class NamedTemporaryFile(object):
    """Context manager for a named temporary file compatible with Windows.

    Provides the path to a closed temporary file that is writeable. Deletes the
    temporary file when exiting the context manager. The built-in
    tempfile.NamedTemporaryFile is not writeable on Windows.
    """
    name = None

    def __enter__(self):
        fh = tempfile.NamedTemporaryFile(delete=False)
        self.name = fh.name
        fh.close()
        return self

    def __exit__(self, type, value, traceback):
        try:
            os.unlink(self.name)
        except:
            pass


class MockedNamespace(object):
    def __init__(self, args):
        self._args = args

    def __getattr__(self, item):
        if self._args.__contains__(item):
            return self._args[item]
        if self.__dict__.__contains__(item):
            return self.__dict__[item]
        return None


class TestingDB:

    def __init__(self, filename):
        self._dir_obj = TempDirectory()
        self.dirpath = self._dir_obj.path
        shutil.copy(
            os.path.join(os.getcwd(), "tests", "samples", "databases", filename),
            os.path.join(self.dirpath, filename)
        )
        self.path = os.path.join(self.dirpath, filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._dir_obj.cleanup()
        except Exception as e:
            pass
