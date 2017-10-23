from unittest.case import TestCase

from turingarena.protocol.plumber.client import Plumber
from turingarena.sandbox.client import Algorithm


class TestPlumber(TestCase):

    def test(self):
        s = Algorithm("solution")
        with s.create_process() as p, Plumber("exampleinterface", process=p):
            pass
