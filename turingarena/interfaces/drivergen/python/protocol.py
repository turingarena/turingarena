from turingarena.interfaces.codegen.utils import indent_all, indent
from turingarena.interfaces.drivergen.python.expression import build_right_value_expression, \
    build_left_value_expression
from turingarena.interfaces.drivergen.python.types import build_type, build_base_type
from turingarena.interfaces.visitor import accept_statement
from ...analysis.types import ScalarType


class AbstractInterfaceGenerator:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def generate_interface(self, interface):
        yield
        yield "@staticmethod"
        yield "def {name}({args}):".format(
            name=self.name,
            args=", ".join(self.args),
        )
        yield from indent_all(self.generate_body(interface))

    def generate_body(self, interface):
        yield from self.generate_interface_begin(interface)

        for statement in interface.statements:
            yield
            yield "# " + statement.info()
            yield from accept_statement(statement, visitor=self)

        yield from self.generate_interface_end(interface)

    def generate_interface_begin(self, interface):
        yield from []

    def generate_interface_end(self, interface):
        yield from []

    def visit_var_statement(self, declaration):
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
                    type=build_type(t),
                )
                for name, t in vars
            )
        )


class ProtocolGenerator(AbstractInterfaceGenerator):
    def generate_interface_begin(self, interface):
        if len(interface.callback_declarations) > 0:
            yield
            yield "def accept_callbacks():"
            yield from indent_all(self.generate_accept_callbacks_body(interface))

    def maybe_accept_callbacks(self, statement):
        interface = statement.outer_block.outer_declaration.interface
        if len(interface.callback_declarations) > 0:
            yield "yield from accept_callbacks()"

    def generate_interface_end(self, interface):
        yield
        yield "return main()"

    def generate_accept_callbacks_body(self, interface):
        if len(interface.callback_declarations) == 0:
            yield "yield from []"
        else:
            yield from self.generate_accept_callbacks_nonempty_body(interface)

    def generate_accept_callbacks_nonempty_body(self, interface):
        yield "while True:"
        yield from indent_all(self.generate_callbacks_loop(interface))

    def generate_callbacks_loop(self, interface):
        yield from self.generate_local_variables([("callback", ScalarType("string"))])
        yield from self.generate_on_callback()
        yield "if get_value(callback_) == 'return': break"
        for decl in interface.callback_declarations:
            yield "elif get_value(callback_) == '{name}': yield from callback_{name}()".format(
                name=decl.declarator.name,
            )
        yield "else: raise ValueError('unexpected callback %s' % get_value(callback_))"

    def generate_on_callback(self):
        yield "pass"

    def visit_function_statement(self, declaration):
        yield "pass"

    def visit_main_statement(self, declaration):
        yield "def main():"
        yield from indent_all(self.generate_main_body(declaration))

    def visit_callback_statement(self, declaration):
        yield "def callback_{name}():".format(name=declaration.declarator.name)
        yield from indent_all(self.generate_callback_body(declaration))

    def generate_main_body(self, declaration):
        yield "# <main initialization>"
        yield from self.generate_main_begin(declaration)
        yield from self.generate_block(declaration.body)
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
        yield from self.generate_block(declaration.body)
        yield "# <callback finalization>"
        yield from self.generate_callback_end(declaration)

    def generate_main_begin(self, declaration):
        yield "pass"

    def generate_main_end(self, declaration):
        # make sure it is a generator
        yield "yield from []"

    def generate_callback_begin(self, declaration):
        yield "pass"

    def generate_callback_end(self, declaration):
        # make sure it is a generator
        yield "yield from []"

    def generate_block(self, block):
        yield "# expected calls: " + str(block.first_calls)
        for statement in block.statements:
            yield "# " + statement.info()
            yield from accept_statement(statement, visitor=self)

    def visit_for_statement(self, statement):
        index_name = statement.index.declarator.name
        yield "for index_{index} in range({range}):".format(
            index=index_name,
            range=build_right_value_expression(statement.index.range),
        )
        yield indent("{index}_ = constant(scalar(int), index_{index})".format(index=index_name))
        yield from indent_all(self.generate_block(statement.body))

    def visit_any_statement(self, statement):
        yield "pass"


class PlumbingProtocolGenerator(ProtocolGenerator):
    """
    Generates the code of a co-routine
    which performs input/output from process stdin/stdout.
    """

    def generate_main_end(self, declaration):
        yield "yield"

    def visit_input_statement(self, statement):
        yield "print({args}, file=downward_pipe, flush=True)".format(
            args=", ".join(
                build_right_value_expression(e)
                for e in statement.arguments
            )
        )

    def generate_on_callback(self):
        yield "read([(str, callback_)], file=upward_pipe)"

    def visit_output_statement(self, statement):
        yield "read([{args}], file=upward_pipe)".format(
            args=", ".join(
                "({type}, {expr})".format(
                    type=build_base_type(a.type),
                    expr=build_left_value_expression(a),
                )
                for a in statement.arguments
            )
        )

    def visit_flush_statement(self, statement):
        yield "yield"

    def visit_call_statement(self, statement):
        yield from self.maybe_accept_callbacks(statement)

    def visit_alloc_statement(self, stmt):
        for a in stmt.arguments:
            yield "{val}.size = {size}".format(
                val=build_left_value_expression(a),
                size=build_right_value_expression(stmt.size),
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
                "{}_, ".format(p.declarator.name)
                for p in declaration.parameters
            ),
        )

    def generate_callback_end(self, declaration):
        yield "yield 'callback_stopped',"

    def visit_for_statement(self, statement):
        if statement.body.first_calls == {None}:
            yield "# suppressed, contains no commands"
            yield "pass"
        else:
            yield from super().visit_for_statement(statement)

    def visit_call_statement(self, statement):
        parameters = statement.function_declaration.parameters
        yield "expect_call(command, '{name}', [{args}])".format(
            name=statement.function_name,
            args=", ".join(
                build_left_value_expression(expr) + ", "
                for p, expr in zip(
                    parameters,
                    statement.parameters
                )
            )
        )
        yield "yield 'call_accepted',"

        yield from self.maybe_accept_callbacks(statement)
        yield "command = yield 'call_returned', '{name}', {ret}".format(
            name=statement.function_name,
            ret="None"
            if statement.return_value is None else
            build_right_value_expression(statement.return_value),
        )

    def visit_flush_statement(self, statement):
        yield "flush()"

    def visit_return_statement(self, stmt):
        yield "expect_return(command, {ret})".format(
            ret=build_left_value_expression(stmt.value)
        )
        yield "yield 'return_accepted',"

    def visit_assignment_statement(self, stmt):
        yield "pass"


class GlobalDataGenerator(AbstractInterfaceGenerator):
    def visit_var_statement(self, declaration):
        yield from super().visit_var_statement(declaration)
        yield "{globals} = {vars}".format(
            globals=", ".join("globals.{}".format(d.name) for d in declaration.declarators),
            vars=", ".join("{}_".format(d.name) for d in declaration.declarators),
        )

    def visit_function_statement(self, declaration):
        yield "pass"

    def visit_callback_statement(self, declaration):
        yield "pass"

    def visit_main_statement(self, declaration):
        yield "pass"


plumbing_generator = PlumbingProtocolGenerator(
    "plumbing", ["var", "upward_pipe", "downward_pipe"])

porcelain_generator = PorcelainProtocolGenerator(
    "porcelain", ["var", "flush"])

global_data_generator = GlobalDataGenerator("global_data", ["var", "globals"])
