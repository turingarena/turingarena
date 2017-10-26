from unittest.case import TestCase

from turingarena.protocol.plumber.client import PlumberClient
from turingarena.sandbox.client import Algorithm


class TestPlumber(TestCase):

    def test(self):
        s = Algorithm("solution")
        with s.sandbox() as p, PlumberClient("exampleinterface", process=p):
            pass
