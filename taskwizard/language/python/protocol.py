from taskwizard.generation.utils import indent_all, indent
from taskwizard.language.python.expression import build_driver_expression
from taskwizard.language.python.types import TypeBuilder


class DriverBlockGenerator:
    def generate(self, item):
        return item.accept(self)

    def visit_block(self, block):
        for item in block.block_items:
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
        yield "if phase == 'upward': yield from self.on_upward_input()"

    def visit_output_statement(self, statement):
        yield "if phase == 'upward': {args}, = self.read_upward({types})".format(
            args=", ".join(build_driver_expression(a) for a in statement.arguments),
            types=", ".join(TypeBuilder().build(a.type) for a in statement.arguments)
        )

    def visit_call_statement(self, statement):
        yield "if phase == 'preflight':"

        def preflight_body():
            yield "{unpack}, = self.get_next_call()".format(
                unpack=", ".join(
                    ["function"] +
                    ["parameter_" + p.declarator.name for p in statement.function_declaration.parameters]
                )
            )
            yield "if function != '{name}': raise ValueError".format(name=statement.function_declaration.declarator.name)
            for p, expr in zip(statement.function_declaration.parameters, statement.parameters):
                yield "{val} = parameter_{name}".format(
                    val=build_driver_expression(expr),
                    name=p.declarator.name,
                )
            yield "yield from self.on_preflight_call()"

        yield from indent_all(preflight_body())
        yield "if phase == 'downward': yield"
        yield "if phase == 'upward': self.on_upward_call()"
        yield "if phase == 'postflight': yield {ret}".format(
            ret="None" if statement.return_value is None else build_driver_expression(statement.return_value),
        )

    def visit_return_statement(self, stmt):
        yield "if phase == 'preflight': {ret} = self.get_last_callback_return()".format(
            ret = build_driver_expression(stmt.expression),
        )

    def visit_alloc_statement(self, stmt):
        yield from []
