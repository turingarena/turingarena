from collections import namedtuple, OrderedDict

from grako.semantics import ModelBuilderSemantics

from taskwizard.definition.function import Function
from taskwizard.definition.interface import Interface
from taskwizard.definition.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase, Protocol

from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.driver import Driver
from taskwizard.definition.expression import IntLiteralExpression, VariableExpression
from taskwizard.definition.test_case import TestCase, TestPhase, TestPhaseSlot
from taskwizard.definition.variable import Variable

Task = namedtuple("Task", ["drivers", "interfaces", "test_cases"])

class Semantics(ModelBuilderSemantics):

    def __init__(self):
        super().__init__(types=[
            Variable,
            Function,
            Driver,
            Interface,
            Protocol,
            InputStep, OutputStep, CallStep,
            ForNode, SwitchNode, SwitchCase,
            VariableExpression, IntLiteralExpression,
            TestCase, TestPhase, TestPhaseSlot
        ])

    def start(self, ast):
        return Task(
            named_definitions(ast.drivers),
            named_definitions(ast.interfaces),
            named_definitions(ast.test_cases))
