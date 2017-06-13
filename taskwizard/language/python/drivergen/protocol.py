from taskwizard.language.python.drivergen.expression import build_driver_expression

from taskwizard.codegen.utils import indent_all, indent
from taskwizard.language.python.drivergen.types import TypeBuilder


class DriverBlockGenerator:
    def generate(self, item):
        return item.accept(self)

    def visit_block(self, block):
        for item in block.block_items:
            yield
            line = item.parseinfo.text_lines()[0]
            yield "# " + line.strip()
            yield from item.accept(self)

    def visit_for_statement(self, statement):
        yield "for {index} in range({start}, {end}):".format(
            index=statement.index.declarator.name,
            start=build_driver_expression(statement.index.range.start),
            end="1 + " + build_driver_expression(statement.index.range.end),
        )
        statements = list(statement.block.accept(self))
        if not statements:
            yield indent("pass")
        else:
            assert any(s is not None for s in statements)
            yield from indent_all(statements)

    def visit_variable_declaration(self, declaration):
        for declarator in declaration.declarators:
            yield "{name} = self.get_local(phase)".format(
                name=declarator.name,
            )

    def visit_input_statement(self, statement):
        yield "if phase == 'downward': print({arguments}, file=self.downward_pipe)".format(
            arguments=", ".join(
                build_driver_expression(e)
                for e in statement.arguments
            )
        )
        yield from generate_upward_maybe_yield()

    def visit_output_statement(self, statement):
        yield "if phase == 'upward': {args}, = self.read_upward({types})".format(
            args=", ".join(build_driver_expression(a) for a in statement.arguments),
            types=", ".join(TypeBuilder().build(a.type) for a in statement.arguments)
        )

    def visit_call_statement(self, statement):
        yield "if phase == 'preflight':"

        def preflight_body():
            yield "{unpack}, = self.expect_call(preflight_command, '{name}')".format(
                unpack=", ".join(
                    "parameter_" + p.declarator.name for p in statement.function_declaration.parameters
                ),
                name = statement.function_name,
            )
            for p, expr in zip(statement.function_declaration.parameters, statement.parameters):
                yield "{val} = parameter_{name}".format(
                    val=build_driver_expression(expr),
                    name=p.declarator.name,
                )
            yield "preflight_command = yield"

        yield from indent_all(preflight_body())
        yield "if phase == 'downward': yield"
        yield "if phase == 'upward': yield from self.upward_lazy_yield()"
        yield "yield from self.accept_callbacks(phase)"
        yield "if phase == 'postflight': yield 'call_return', {ret}".format(
            ret="None" if statement.return_value is None else build_driver_expression(statement.return_value),
        )

    def visit_return_statement(self, stmt):
        yield "if phase == 'preflight':"
        def body():
            yield "{ret} = self.expect_callback_return(preflight_command)".format(
                ret = build_driver_expression(stmt.expression),
            )
            yield "preflight_command = yield"
        yield from indent_all(body())

        yield "if phase == 'downward': yield"
        yield "if phase == 'upward': yield from self.upward_lazy_yield()"


    def visit_alloc_statement(self, stmt):
        yield "if phase == 'downward':"
        def body():
            for a in stmt.arguments:
                yield "assert ({val}.start, {val}.end) == ({start}, {end})".format(
                    val=build_driver_expression(a),
                    start=build_driver_expression(stmt.range.start),
                    end=build_driver_expression(stmt.range.end),
                )
        yield from indent_all(body())


def generate_upward_maybe_yield():
    yield "if phase == 'upward': yield from self.upward_maybe_yield()"


def generate_main_block(declaration):
    yield "if phase == 'preflight': preflight_command = yield 'initial_command'"
    yield from DriverBlockGenerator().generate(declaration.block)
    yield
    yield "# ensure last upward lazy yield is done"
    yield from generate_upward_maybe_yield()


def generate_callback_block(decl):
    yield "if phase == 'preflight': preflight_command = yield 'initial_command'"
    yield "{parameters} = {locals}".format(
        parameters=", ".join(p.declarator.name for p in decl.parameters),
        locals=", ".join("self.get_local(phase)" for p in decl.parameters),
    )
    yield "if phase == 'postflight': yield 'callback', '{name}', ({args})".format(
        name=decl.declarator.name,
        args="".join(
            "{}.value, ".format(p.declarator.name)
            for p in decl.parameters
        ),
    )
    yield from DriverBlockGenerator().generate(decl.block)
