from collections import namedtuple, OrderedDict
from jinja2 import Template
from taskwizard.compiler.grammar import GrammarParser


class Variable(namedtuple("Variable", [
        "name", "type", "is_input", "is_output"
])):
    pass


class Parameter(namedtuple("Parameter", ["name", "type"])):
    pass


class Function(namedtuple("Function", ["name", "return_type", "parameters"])):
    pass


class CallbackFunction(Function):
    is_callback = True

    pass


class Algorithm(namedtuple("Algorithm", [
        "name", "variables", "functions", "callback_functions"
])):

    @classmethod
    def create(cls, name, declarations):
        variables = OrderedDict()
        functions = OrderedDict()
        callback_functions = OrderedDict()

        for declaration in declarations:
            if isinstance(declaration, Variable):
                container = variables
            elif isinstance(declaration, CallbackFunction):
                container = callback_functions
            elif isinstance(declaration, Function):
                container = functions
            container[declaration.name] = declaration

        return cls(name, variables, functions, callback_functions)


class Semantics:

    def algorithm(self, ast):
        return Algorithm.create(ast.name, ast.declarations)

    def variable_declaration(self, ast):
        return Variable(
            ast.name,
            ast.type,
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
        return Parameter(ast.name, ast.type)

    def _default(self, ast):
        return ast


def main():
    parse = GrammarParser(semantics=Semantics())
    text = open("tests/test.task").read()
    algorithm = parse.parse(text)

    stub_template_text = open("taskwizard/compiler/stub_template.cpp.jinja2").read()
    stub_template = Template(stub_template_text)

    print(stub_template.render(algorithm=algorithm))

    support_template_text = open("taskwizard/compiler/support_template.cpp.jinja2").read()
    support_template = Template(support_template_text)

    print(support_template.render(algorithm=algorithm))
