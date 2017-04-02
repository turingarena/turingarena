from collections import namedtuple, OrderedDict

from grako.semantics import ModelBuilderSemantics

from taskwizard.declarations import named_definitions
from taskwizard.driver import Driver
from taskwizard.expr import IntLiteralExpression
from taskwizard.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase

Variable = namedtuple("Variable", ["name", "type", "array_dimensions"])
GlobalVariable = namedtuple("GlobalVariable", [*Variable._fields, "is_input", "is_output"])
Parameter = namedtuple("Parameter", [*Variable._fields])
Function = namedtuple("Function", ["name", "return_type", "parameters"])
Interface = namedtuple("Interface", ["name", "variables", "functions", "callback_functions", "protocols"])
Scenario = namedtuple("Scenario", ["name", "phases"])
Phase = namedtuple("Phase", ["name", "driver_name", "driver_command", "slots"])
Task = namedtuple("Task", ["drivers", "interfaces", "scenarios"])
Slot = namedtuple("Slot", ["name", "interface_name"])


class CallbackFunction(Function):
    is_callback = True


class Semantics(ModelBuilderSemantics):

    def __init__(self):
        super().__init__(types=[
            Driver,
            InputStep, OutputStep, CallStep,
            ForNode, SwitchNode, SwitchCase
        ])

    def start(self, ast):
        return Task(
            named_definitions(ast.drivers),
            named_definitions(ast.interfaces),
            named_definitions(ast.scenarios))

    def scenario_definition(self, ast):
        return Scenario(ast.name, named_definitions(ast.phases))

    def phase_definition(self, ast):
        return Phase(ast.name, ast.driver_name, ast.driver_command, named_definitions(ast.slots))

    def slot_definition(self, ast):
        return Slot(ast.name, ast.interface_name)

    def interface_definition(self, ast):
        return Interface(
            ast.name,
            named_definitions(ast.variables),
            named_definitions(ast.functions),
            named_definitions(ast.callback_functions),
            named_definitions(ast.protocols)
        )

    def variable_declaration(self, ast):
        return Variable(ast.name, ast.type, ast.array_dimensions)

    def array_dimension(self, ast):
        if ast.constant is not None:
            return ast.constant
        else:
            return ast.variable_reference

    def global_variable_declaration(self, ast):
        return GlobalVariable(
            *ast.variable,
            is_input=(ast.inout in ["in", "inout"]),
            is_output=(ast.inout in ["out", "inout"])
        )

    def function_declaration(self, ast):
        parameters = OrderedDict()

        for parameter in ast.parameters:
            parameters[parameter.name] = parameter

        return (CallbackFunction if ast.callback is not None else Function)(
            ast.name, ast.return_type, OrderedDict(parameters)
        )

    def parameter(self, ast):
        return Parameter(*ast.variable)

    def int_literal_expr(self, ast):
        return IntLiteralExpression(ast)
