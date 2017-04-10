import unittest

from taskwizard.definition.semantics import Semantics

from taskwizard.language.cpp.codegen import CodeGenerator
from taskwizard.parser import TaskParser

parser = TaskParser(semantics=Semantics())


class TestCodeGeneratorCpp(unittest.TestCase):

    def test_interface_support(self):
        task = parser.parse(open("test_task.txt").read())
        interface = task.interfaces["exampleinterface"]

        expected_code = open("expected/interface_support.cpp").read()
        code = '\n'.join(CodeGenerator().generate_interface_support(interface)) + '\n'
        self.assertEqual(expected_code, code)

    def test_driver_support(self):
        task = parser.parse(open("test_task.txt").read())
        interface = task.interfaces["exampleinterface"]

        code = '\n'.join(CodeGenerator().generate_interface_driver_support(interface)) + '\n'
        expected_code = open("expected/driver.h").read()
        self.assertEqual(expected_code, code)
