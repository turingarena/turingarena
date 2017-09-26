from collections import OrderedDict

from turingarena.interfaces.codegen.utils import indent_all, indent
from turingarena.interfaces.drivergen.python.expression import build_driver_expression, \
    build_assignable_expression
from turingarena.interfaces.drivergen.python.types import TypeBuilder, BaseTypeBuilder
from ...analysis.types import ScalarType


class AbstractInterfaceGenerator:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def generate(self, item):
        yield from item.accept(self)

    def visit_interface_definition(self, interface):
        yield
        yield "@staticmethod"
        yield "def {name}({args}):".format(
            name=self.name,
            args=", ".join(self.args),
        )
        yield from indent_all(self.generate_body(interface))

    def generate_body(self, interface):
        yield from self.generate_interface_begin(interface)

        for item in interface.interface_items:
            yield
            yield "# " + item.info()
            yield from self.generate(item)

        yield from self.generate_interface_end(interface)

    def generate_interface_begin(self, interface):
        yield from []

    def generate_interface_end(self, interface):
        yield from []

    def visit_variable_declaration(self, declaration):
        yield from self.generate_local_variables(
            (d.name, declaration.type) for d in declaration.declarators
        )

    def generate_local_variables(self, vars):
        vars = list(vars)
        assert len(vars) >= 1

        vars = list(vars)
        yield "{names}, = {creators},".format(
            names=", ".join(name + "_" for name, t in vars),
            creators=", ".join(
                "var({type})".format(
                    type=TypeBuilder().build(t),
                )
                for name, t in vars
            )
        )


class ProtocolGenerator(AbstractInterfaceGenerator):
    def generate_interface_begin(self, interface):
        yield
        yield "def accept_callbacks():"
        yield from indent_all(self.generate_accept_callbacks_body(interface))

    def generate_interface_end(self, interface):
        yield
        yield "return main()"

    def generate_accept_callbacks_body(self, interface):
        if len(interface.callback_declarations) == 0:
            yield "pass"
        else:
            yield from self.generate_accept_callbacks_nonempty_body(interface)

    def generate_accept_callbacks_nonempty_body(self, interface):
        yield "while True:"
        yield from indent_all(self.generate_callbacks_loop(interface))

    def generate_callbacks_loop(self, interface):
        yield from self.generate_local_variables([("callback", ScalarType("string"))])
        yield from self.generate_on_callback()
        yield "if callback_[:] == 'return': break"
        for decl in interface.callback_declarations:
            yield "elif callback_[:] == '{name}': yield from callback_{name}()".format(
                name=decl.declarator.name,
            )
        yield "else: raise ValueError('unexpected callback %s' % callback_[:])"

    def generate_on_callback(self):
        yield "pass"

    def visit_function_declaration(self, declaration):
        yield "pass"

    def visit_main_declaration(self, declaration):
        yield "def main():"
        yield from indent_all(self.generate_main_body(declaration))

    def visit_callback_declaration(self, declaration):
        yield "def callback_{name}():".format(name=declaration.declarator.name)
        yield from indent_all(self.generate_callback_body(declaration))

    def generate_main_body(self, declaration):
        yield "# <main initialization>"
        yield from self.generate_main_begin(declaration)
        yield from self.generate(declaration.block)
        yield "# <main finalization>"
        yield from self.generate_main_end(declaration)

    def generate_callback_body(self, declaration):
        if len(declaration.parameters) >= 1:
            yield "# <callback arguments>"
            yield from self.generate_local_variables(
                (p.declarator.name, p.type) for p in declaration.parameters
            )
        yield "# <callback initialization>"
        yield from self.generate_callback_begin(declaration)
        yield from self.generate(declaration.block)
        yield "# <callback finalization>"
        yield from self.generate_callback_end(declaration)

    def generate_main_begin(self, declaration):
        yield "pass"

    def generate_main_end(self, declaration):
        yield "pass"

    def generate_callback_begin(self, declaration):
        yield "pass"

    def generate_callback_end(self, declaration):
        yield "pass"

    def visit_block(self, block):
        yield "# expected calls: " + str(block.first_calls)
        for item in block.block_items:
            yield "# " + item.info()
            yield from item.accept(self)

    def visit_for_statement(self, statement):
        index_name = statement.index.declarator.name
        yield "for index_{index} in range({start}, {end}):".format(
            index=index_name,
            start=build_driver_expression(statement.index.range.start),
            end="1 + " + build_driver_expression(statement.index.range.end),
        )
        yield indent("{index}_ = constant(scalar(int), index_{index})".format(index=index_name))
        yield from indent_all(self.generate(statement.block))

    def visit_default(self, stmt):
        yield "pass"


class PlumbingProtocolGenerator(ProtocolGenerator):
    """
    Generates the code of a co-routine
    which performs input/output from process stdin/stdout.
    """

    def generate_main_end(self, declaration):
        yield "yield"

    def visit_input_statement(self, statement):
        yield "print({arguments}, file=downward_pipe, flush=True)".format(
            arguments=", ".join(
                build_driver_expression(e)
                for e in statement.arguments
            )
        )

    def generate_on_callback(self):
        yield "callback_[:], = read([str], file=upward_pipe)"

    def visit_output_statement(self, statement):
        yield "{args}, = read([{types}], file=upward_pipe)".format(
            args=", ".join(build_assignable_expression(a) for a in statement.arguments),
            types=", ".join(BaseTypeBuilder().build(a.type) for a in statement.arguments)
        )

    def visit_flush_statement(self, statement):
        yield "yield"

    def visit_call_statement(self, statement):
        yield "yield from accept_callbacks()"

    def visit_alloc_statement(self, stmt):
        for a in stmt.arguments:
            yield "{val}.range = ({start}, {end})".format(
                val=build_driver_expression(a),
                start=build_driver_expression(stmt.range.start),
                end=build_driver_expression(stmt.range.end),
            )


class PorcelainProtocolGenerator(ProtocolGenerator):
    """
    Generates the code of a co-routine
    which processes call/callback/return events.
    """
    def generate_main_begin(self, declaration):
        yield "command = yield 'main_started',"

    def generate_main_end(self, declaration):
        yield "yield 'main_stopped',"

    def generate_callback_begin(self, declaration):
        yield "command = yield 'callback_started', '{name}', ({args})".format(
            name=declaration.declarator.name,
            args="".join(
                "{}_[:], ".format(p.declarator.name)
                for p in declaration.parameters
            ),
        )

    def generate_callback_end(self, declaration):
        yield "yield 'callback_stopped',"

    def visit_for_statement(self, statement):
        if statement.block.first_calls == {None}:
            yield "# suppressed, contains no commands"
            yield "pass"
        else:
            yield from super().visit_for_statement(statement)

    def visit_call_statement(self, statement):
        yield "{unpack}, = expect_call(command, '{name}')".format(
            unpack=", ".join(
                build_assignable_expression(expr)
                for p, expr in zip(
                    statement.function_declaration.parameters,
                    statement.parameters
                )
            ),
            name=statement.function_name,
        )
        yield "yield 'call_accepted',"
        yield "yield from accept_callbacks()"
        yield "command = yield 'call_returned', '{name}', {ret}".format(
            name=statement.function_name,
            ret="None"
            if statement.return_value is None else
            build_driver_expression(statement.return_value),
        )

    def visit_flush_statement(self, statement):
        yield "flush()"

    def visit_return_statement(self, stmt):
        yield "{ret} = expect_return(command)".format(
            ret=build_assignable_expression(stmt.expression)
        )
        yield "yield 'return_accepted',"


class GlobalDataGenerator(AbstractInterfaceGenerator):
    def visit_variable_declaration(self, declaration):
        yield from super().visit_variable_declaration(declaration)
        yield "{globals} = {vars}".format(
            globals=", ".join("globals.{}".format(d.name) for d in declaration.declarators),
            vars=", ".join("{}_".format(d.name) for d in declaration.declarators),
        )

    def visit_function_declaration(self, declaration):
        yield "pass"

    def visit_callback_declaration(self, declaration):
        yield "pass"

    def visit_main_declaration(self, declaration):
        yield "pass"


plumbing_generator = PlumbingProtocolGenerator(
    "plumbing", ["var", "upward_pipe", "downward_pipe"])

porcelain_generator = PorcelainProtocolGenerator(
    "porcelain", ["var", "flush"])

global_data_generator = GlobalDataGenerator("global_data", ["var", "globals"])
