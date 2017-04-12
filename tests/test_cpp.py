import unittest

import pkg_resources

from taskwizard.definition.task import TaskDefinition, Task
from taskwizard.language.cpp.codegen import CodeGenerator


test_task_filename = "tests/test_task.txt"
task_definition_text = open(test_task_filename).read()


class TestCodeGeneratorCpp(unittest.TestCase):

    def test_interface_support(self):
        task = Task(TaskDefinition.parse(task_definition_text))
        interface = task.interfaces["exampleinterface"]

        expected_code = open("tests/expected/interface_support.cpp").read()
        code = '\n'.join(CodeGenerator().generate_interface_support(interface)) + '\n'
        self.assertEqual(expected_code, code)

    def test_driver_support(self):
        task = Task(TaskDefinition.parse(task_definition_text))
        interface = task.interfaces["exampleinterface"]

        code = '\n'.join(CodeGenerator().generate_interface_driver_support(interface)) + '\n'
        expected_code = open("tests/expected/driver.h").read()
        self.assertEqual(expected_code, code)
