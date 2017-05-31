from taskwizard.generation.statements import StatementVisitor
from taskwizard.language.cpp import blocks
from taskwizard.language.cpp.expressions import generate_expression
from taskwizard.language.cpp.formats import generate_format
from taskwizard.language.cpp.utils import indent


class StatementGenerator(StatementVisitor):

    def __init__(self, scope):
        self.scope = scope

    def visit_for_statement(self, statement):
        yield 'for(int {index} = {start}; {index} <= {end}; {index}++)'.format(
                index=statement.index,
                start=generate_expression(statement.range.start),
                end=generate_expression(statement.range.end)
        ) + " {"
        yield from indent(blocks.generate_block(statement.block, self.scope))
        yield "}"

    def visit_input_statement(self, statement):
        format_string = ''.join(generate_format(v, self.scope) for v in statement.arguments)
        args = ', '.join("&" + generate_expression(v) for v in statement.arguments)

        yield 'scanf("{format}", {args});'.format(format=format_string, args=args)

    def visit_output_statement(self, node):
        format_string = ' '.join(generate_format(v, self.scope) for v in node.arguments) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.arguments)

        yield 'printf("{format}", {args});'.format(format=format_string, args=args)

    def visit_call_statement(self, node):
        if node.return_value is not None:
            return_value = generate_expression(node.return_value) + " = "
        else:
            return_value = ""

        yield "{return_value}{function_name}({parameters});".format(
            return_value=return_value,
            function_name=node.function_name,
            parameters=", ".join(generate_expression(p) for p in node.parameters)
        )



def generate_statement(statement, scope):
    return StatementGenerator(scope).visit(statement)
