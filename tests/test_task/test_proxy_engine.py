from contextlib import contextmanager
from io import StringIO
from unittest.case import TestCase

from turingarena.protocol.proxy.python.library import *


class D: pass


@contextmanager
def rewinding(stream):
    pos = stream.tell()
    yield stream
    stream.seek(pos)


class TestProxyEngine(TestCase):
    def check_communication(self, request, response, command=None, retval=None):
        with rewinding(self.engine.response_pipe):
            for line in response:
                print(line, file=self.engine.response_pipe)
        actual_retval = None
        if command:
            with rewinding(self.engine.request_pipe):
                actual_retval = command()
        for line in request:
            self.assertEqual(line, self.engine.request_pipe.readline().strip())
        self.assertFalse(self.engine.request_pipe.readline())
        if retval:
            self.assertEqual(retval, actual_retval)

    def setUp(self):
        self.data = D()
        self.data.N = 10
        self.data.A = []
        self.engine = ProxyEngine(
            interface=[
                interface_var(scalar(int), ["N"]),
                interface_var(array(scalar(int)), ["A"]),
                interface_function(signature("solve", [arg(scalar(int), "x")], None)),
                interface_function(signature("solve2", [arg(scalar(int), "x")], scalar(int))),
                interface_callback(signature("cb", [arg(scalar(int), "y")], scalar(int))),
            ],
            instance=self.data,
            request_pipe=StringIO(),
            response_pipe=StringIO(),
        )

    def test_unexpected_callbacks(self):
        self.check_communication(
            [
                "globals", "10", "0",
                "call", "solve", "0", "15",
            ],
            ["function_stop"],
            lambda: self.engine.call("solve", [15], {}),
        )

    def test_no_callbacks(self):
        self.check_communication(
            [
                "globals", "10", "0",
                "call", "solve", "1", "15",
            ],
            ["no_callbacks", "function_stop"],
            lambda: self.engine.call("solve", [15], {"cb": lambda y: y + 1}),
        )

    def test_callbacks(self):
        self.check_communication(
            [
                "globals", "10", "0",
                "call", "solve", "1", "15",
                "callback_stop", "callback_return", "8",
            ],
            ["callback", "cb", "7", "no_callbacks", "function_stop"],
            lambda: self.engine.call("solve", [15], {"cb": lambda y: y + 1}),
        )

    def test_return_value(self):
        self.check_communication(
            [
                "globals", "10", "0",
                "call", "solve2", "0", "15",
            ],
            ["function_stop", "function_return", "30"],
            lambda: self.engine.call("solve2", [15], {}),
            30,
        )

    def test_global_array(self):
        self.data.A = [11, 12, 13]
        self.check_communication(
            [
                "globals", "10", "3", "11", "12", "13",
                "call", "solve", "0", "15",
            ],
            ["function_stop"],
            lambda: self.engine.call("solve", [15], {}),
        )

