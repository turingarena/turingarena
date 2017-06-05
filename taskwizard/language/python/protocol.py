from taskwizard.generation.utils import indent_all
from taskwizard.language.python.expression import build_driver_expression, build_assignable_driver_expression


class BlockDriverGenerator:

    def generate(self, item):
        return item.accept(self)

    def visit_local_declaration(self, declaration):
        yield
        for declarator in declaration.declarators:
            yield "{name} = None".format(
                name=declarator.name,
            )

    def visit_input_statement(self, statement):
        yield
        yield "print({arguments}, file=self.downward_pipe)".format(
            arguments=", ".join(
                build_driver_expression(e)
                for e in statement.arguments
            )
        )

    def visit_output_statement(self, statement):
        yield
        yield "_values = self.upward_pipe.readline().split()"
        for i, argument in enumerate(statement.arguments):
            yield "{arg} = int(_values[{i}])".format(
                arg=build_driver_expression(argument),
                i=i,
            )

    def visit_alloc_statement(self, statement):
        return []

    def visit_call_statement(self, statement):
        yield
        yield "{unpack} = next_call".format(
            unpack=", ".join(
                ["function"] +
                ["parameter_" + p.declarator.name for p in statement.function_declaration.parameters]
            )
        )
        yield "if function != '{name}': raise ValueError".format(name=statement.function_declaration.declarator.name)
        for p, expr in zip(statement.function_declaration.parameters, statement.parameters):
            yield "if not is_set({val}): {val} = set_value({val}, parameter_{name})".format(
                val=build_assignable_driver_expression(expr),
                name=p.declarator.name,
            )

    def visit_for_statement(self, statement):
        yield
        yield "for {index} in range({start}, {end}):".format(
            index=statement.index.declarator.name,
            start=build_driver_expression(statement.index.range.start),
            end="1 + " + build_driver_expression(statement.index.range.end),
        )
        yield from indent_all(generate_driver_block(statement.block))


def generate_driver_block(block):
    generator = BlockDriverGenerator()
    for item in block.block_items:
        yield from item.accept(generator)

