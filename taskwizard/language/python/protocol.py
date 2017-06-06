from taskwizard.generation.utils import indent_all, indent
from taskwizard.language.python.expression import build_driver_expression, build_assignable_driver_expression


class AbstractDriverGenerator:

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

    def visit_default(self, stmt):
        yield from []


class PreflightDriverBlockGenerator(AbstractDriverGenerator):

    def visit_local_declaration(self, declaration):
        for declarator in declaration.declarators:
            yield "{name} = self.make_local()".format(
                name=declarator.name,
            )

    def visit_call_statement(self, statement):
        yield "{unpack}, = self.get_next_call()".format(
            unpack=", ".join(
                ["function"] +
                ["parameter_" + p.declarator.name for p in statement.function_declaration.parameters]
            )
        )
        yield "if function != '{name}': raise ValueError".format(name=statement.function_declaration.declarator.name)
        for p, expr in zip(statement.function_declaration.parameters, statement.parameters):
            yield "{val} = parameter_{name}".format(
                val=build_assignable_driver_expression(expr),
                name=p.declarator.name,
            )
        yield "yield from self.on_preflight_call()"


class DownwardDriverBlockGenerator(AbstractDriverGenerator):

    def visit_local_declaration(self, declaration):
        for declarator in declaration.declarators:
            yield "{name} = self.get_downward_local()".format(
                name=declarator.name,
            )

    def visit_input_statement(self, statement):
        yield "print({arguments}, file=self.downward_pipe)".format(
            arguments=", ".join(
                build_driver_expression(e)
                for e in statement.arguments
            )
        )

    def visit_call_statement(self, statement):
        yield "yield"


class UpwardDriverBlockGenerator(AbstractDriverGenerator):

    def visit_local_declaration(self, declaration):
        for declarator in declaration.declarators:
            yield "{name} = self.get_upward_local()".format(
                name=declarator.name,
            )

    def visit_output_statement(self, statement):
        yield "{args}, = self.read_upward({types})".format(
            args=", ".join(build_driver_expression(a) for a in statement.arguments),
            types=", ".join("int" for a in statement.arguments) # TODO: correct typing
        )

    def visit_input_statement(self, stmt):
        yield "yield from self.on_upward_input()"

    def visit_call_statement(self, statement):
        yield "self.on_upward_call()"


class PostflightDriverBlockGenerator(AbstractDriverGenerator):

    def visit_local_declaration(self, declaration):
        for declarator in declaration.declarators:
            yield "{name} = self.get_postflight_local()".format(
                name=declarator.name,
            )

    def visit_call_statement(self, statement):
        yield "yield {ret}".format(
            ret="None" if statement.return_value is None else build_driver_expression(statement.return_value),
        )
