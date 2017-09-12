from abc import abstractmethod
from collections import OrderedDict

from turingarena.compiler.analysis.types import ScalarType

from turingarena.language.python.compiler.runtimegen.expression import build_driver_expression, \
    build_assignable_expression

from turingarena.compiler.codegen.utils import indent_all, indent
from turingarena.language.python.compiler.runtimegen.types import TypeBuilder, BaseTypeBuilder


class AbstractInterfaceGenerator:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def generate(self, item):
        yield from item.accept(self)

    def visit_interface_definition(self, interface):
        yield
        yield
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
        yield "yield"

    def visit_function_declaration(self, declaration):
        yield "pass"

    def visit_main_declaration(self, declaration):
        yield "def main():"
        yield from indent_all(self.generate_main_body(declaration))

    def visit_callback_declaration(self, declaration):
        yield "def callback_{name}():".format(name=declaration.declarator.name)
        yield from indent_all(self.generate_callback_body(declaration))

    def generate_main_body(self, declaration):
        yield "# <initialization>"
        yield from self.generate_main_begin(declaration)
        yield from self.generate(declaration.block)

    def generate_callback_body(self, declaration):
        yield "# <arguments>"
        yield from self.generate_local_variables(
            (p.declarator.name, p.type) for p in declaration.parameters
        )
        yield "# <initialization>"
        yield from self.generate_callback_begin(declaration)
        yield from self.generate(declaration.block)

    def generate_main_begin(self, declaration):
        yield "pass"

    def generate_callback_begin(self, declaration):
        yield "pass"

    def visit_block(self, block):
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
        yield indent("{index}_ = var(scalar(int), index_{index})".format(index=index_name))
        yield from indent_all(self.generate(statement.block))

    def visit_default(self, stmt):
        yield "pass"


class UpwardDataGenerator(ProtocolGenerator):
    def generate_on_callback(self):
        yield "callback_[:], = read([str], file=pipe)"
        yield "yield"

    def generate_main_begin(self, declaration):
        yield from self.lazy_yield()

    def generate_callback_begin(self, declaration):
        yield from self.lazy_yield()

    def visit_input_statement(self, statement):
        yield from self.maybe_yield()

    def visit_call_statement(self, statement):
        yield from self.maybe_yield()
        yield from self.lazy_yield()
        yield "yield from accept_callbacks()"

    def maybe_yield(self):
        yield "yield from to_yield"

    def lazy_yield(self):
        yield "to_yield = lazy_yield()"

    def visit_return_statement(self, stmt):
        yield from self.maybe_yield()

    def visit_output_statement(self, statement):
        yield "{args}, = read([{types}], file=pipe)".format(
            args=", ".join(build_assignable_expression(a) for a in statement.arguments),
            types=", ".join(BaseTypeBuilder().build(a.type) for a in statement.arguments)
        )


class UpwardControlGenerator(ProtocolGenerator):
    def generate_main_begin(self, declaration):
        yield "yield 'main',"

    def generate_callback_begin(self, declaration):
        yield "yield 'callback', '{name}', ({args})".format(
            name=declaration.declarator.name,
            args="".join(
                "{}_[:], ".format(p.declarator.name)
                for p in declaration.parameters
            ),
        )

    def visit_call_statement(self, statement):
        yield "yield from accept_callbacks()"
        yield "yield 'call_return', '{name}', {ret}".format(
            name=statement.function_name,
            ret="None"
            if statement.return_value is None else
            build_driver_expression(statement.return_value),
        )


class DownwardControlGenerator(ProtocolGenerator):
    def generate_main_begin(self, declaration):
        yield "command = yield"

    def generate_callback_begin(self, declaration):
        yield "command = yield"

    def visit_return_statement(self, stmt):
        yield "{ret}expect_return(command)".format(
            ret=(
                "" if stmt.expression is None else
                build_driver_expression(stmt.expression) + " = "
            )
        )
        yield "yield"

    def visit_call_statement(self, statement):
        yield "{unpack}, = expect_call(command, '{name}')".format(
            unpack=", ".join(
                "parameter_" + p.declarator.name for p in statement.function_declaration.parameters
            ),
            name=statement.function_name,
        )
        for p, expr in zip(statement.function_declaration.parameters, statement.parameters):
            yield "{val} = parameter_{name}".format(
                val=build_assignable_expression(expr),
                name=p.declarator.name,
            )
        yield "yield from accept_callbacks()"
        yield "command = yield"


class DownwardDataGenerator(ProtocolGenerator):

    def visit_input_statement(self, statement):
        yield "print({arguments}, file=pipe)".format(
            arguments=", ".join(
                build_driver_expression(e)
                for e in statement.arguments
            )
        )

    def visit_call_statement(self, statement):
        yield "yield"
        yield "yield from accept_callbacks()"

    def visit_alloc_statement(self, stmt):
        for a in stmt.arguments:
            yield "assert ({val}.start, {val}.end) == ({start}, {end})".format(
                val=build_driver_expression(a),
                start=build_driver_expression(stmt.range.start),
                end=build_driver_expression(stmt.range.end),
            )

    def visit_return_statement(self, statement):
        yield "yield"


class GlobalDataGenerator(AbstractInterfaceGenerator):

    def visit_interface_definition(self, interface):
        yield
        yield
        yield "def global_data(var, globals):"
        yield from indent_all(self.generate_body(interface))

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


protocol_generators = OrderedDict(
    (g.name, g)
    for g in [
        UpwardDataGenerator("upward_data", ["var", "pipe"]),
        UpwardControlGenerator("upward_control", ["var"]),
        DownwardControlGenerator("downward_control", ["var"]),
        DownwardDataGenerator("downward_data", ["var", "pipe"]),
    ]
)

global_data_generator = GlobalDataGenerator("global_data", ["var", "globals"])