from collections import namedtuple, OrderedDict

Variable = namedtuple("Variable", ["name", "type", "array_dimensions"])
GlobalVariable = namedtuple("GlobalVariable", [*Variable._fields, "is_input", "is_output"])
Parameter = namedtuple("Parameter", [*Variable._fields])
Function = namedtuple("Function", ["name", "return_type", "parameters"])
Command = namedtuple("Command", [])
Interface = namedtuple("Interface", ["name", "variables", "functions", "callback_functions"])
Driver = namedtuple("Interface", ["name", "variables", "functions"])
Scenario = namedtuple("Scenario", ["name", "phases"])
Phase = namedtuple("Phase", ["name", "driver_name", "driver_command", "slots"])
Task = namedtuple("Task", ["drivers", "interfaces", "scenarios"])
Slot = namedtuple("Slot", ["name", "interface_name"])


class CallbackFunction(Function):
    is_callback = True


class Semantics:

    def named_definitions(self, definitions):
        result = OrderedDict()
        for d in definitions:
            result[d.name] = d
        return result

    def start(self, ast):
        return Task(
            self.named_definitions(ast.drivers),
            self.named_definitions(ast.interfaces),
            self.named_definitions(ast.scenarios))

    def scenario_definition(self, ast):
        return Scenario(ast.name, self.named_definitions(ast.phases))

    def phase_definition(self, ast):
        return Phase(ast.name, ast.driver_name, ast.driver_command, self.named_definitions(ast.slots))

    def slot_definition(self, ast):
        return Slot(ast.name, ast.interface_name)

    def driver_definition(self, ast):
        return Driver(
            ast.name,
            self.named_definitions(ast.variables),
            self.named_definitions(ast.functions))

    def interface_definition(self, ast):
        return Interface(
            ast.name,
            self.named_definitions(ast.variables),
            self.named_definitions(ast.functions),
            self.named_definitions(ast.callback_functions))

    def variable(self, ast):
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

    def _default(self, ast):
        return ast
