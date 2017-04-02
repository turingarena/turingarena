from collections import namedtuple, OrderedDict

from grako.semantics import ModelBuilderSemantics
from taskwizard.definition.interface import Interface
from taskwizard.definition.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase

from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.driver import Driver
from taskwizard.definition.expr import IntLiteralExpression
from taskwizard.definition.variable import Variable

Function = namedtuple("Function", ["name", "return_type", "parameters"])
TestCase = namedtuple("TestCase", ["name", "phases"])
TestPhase = namedtuple("TestPhase", ["name", "driver_name", "driver_command", "slots"])
Task = namedtuple("Task", ["drivers", "interfaces", "test_cases"])
Slot = namedtuple("Slot", ["name", "interface_name"])


class CallbackFunction(Function):
    is_callback = True


class Semantics(ModelBuilderSemantics):

    def __init__(self):
        super().__init__(types=[
            Variable,
            Driver,
            Interface,
            InputStep, OutputStep, CallStep,
            ForNode, SwitchNode, SwitchCase,
            IntLiteralExpression
        ])

    def start(self, ast):
        return Task(
            named_definitions(ast.drivers),
            named_definitions(ast.interfaces),
            named_definitions(ast.test_cases))

    def test_case_definition(self, ast):
        return TestCase(ast.name, named_definitions(ast.phases))

    def test_phase_definition(self, ast):
        return TestPhase(ast.name, ast.driver_name, ast.driver_command, named_definitions(ast.slots))

    def slot_definition(self, ast):
        return Slot(ast.name, ast.interface_name)

    def array_dimension(self, ast):
        if ast.constant is not None:
            return ast.constant
        else:
            return ast.variable_reference

    def function_declaration(self, ast):
        parameters = OrderedDict()

        for parameter in ast.parameters:
            parameters[parameter.name] = parameter

        return (CallbackFunction if ast.callback is not None else Function)(
            ast.name, ast.return_type, OrderedDict(parameters)
        )
