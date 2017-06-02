from taskwizard.generation.expressions import extract_type
from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import indent_all
from taskwizard.grammar import SyntaxVisitor
from taskwizard.language.cpp.declarations import build_declaration, generate_declarators
from taskwizard.language.cpp.expressions import generate_expression
from taskwizard.language.cpp.types import generate_base_type


def generate_format(expression, scope):
    type = extract_type(scope, expression)
    return {
        "int": "%d",
        "int64": "%lld",
    }[type.base]


class BlockGenerator(SyntaxVisitor):

    def __init__(self, external_scope):
        self.scope = Scope(external_scope)

    def __init__(self, scope):
        self.scope = scope

    # TODO: add index to scope
    def visit_for_statement(self, statement):
        yield 'for(int {index} = {start}; {index} <= {end}; {index}++)'.format(
                index=statement.index.declarator.name,
                start=generate_expression(self.scope, statement.index.range.start),
                end=generate_expression(self.scope, statement.index.range.end)
        ) + " {"
        new_scope = Scope(self.scope)
        new_scope.process_simple_declaration(statement.index)
        yield from indent_all(generate_block(statement.block, new_scope))
        yield "}"

    def visit_input_statement(self, statement):
        format_string = ''.join(generate_format(v, self.scope) for v in statement.arguments)
        args = ', '.join("&" + generate_expression(self.scope, v) for v in statement.arguments)

        yield 'scanf("{format}", {args});'.format(format=format_string, args=args)

    def visit_output_statement(self, node):
        format_string = ' '.join(generate_format(v, self.scope) for v in node.arguments) + r'\n'
        args = ', '.join(generate_expression(self.scope, v) for v in node.arguments)

        yield 'printf("{format}", {args});'.format(format=format_string, args=args)

    def visit_call_statement(self, node):
        if node.return_value is not None:
            return_value = generate_expression(self.scope, node.return_value) + " = "
        else:
            return_value = ""

        yield "{return_value}{function_name}({parameters});".format(
            return_value=return_value,
            function_name=node.function_name,
            parameters=", ".join(generate_expression(self.scope, p) for p in node.parameters)
        )

    def visit_alloc_statement(self, statement):
        for argument in statement.arguments:
            yield "{var} = new {type}[{size}];".format(
                var=generate_expression(self.scope, argument),
                type=generate_base_type(extract_type(self.scope, argument)),
                size="1 + " + generate_expression(self.scope, statement.range.end),
            )

    def visit_local_declaration(self, declaration):
        yield build_declaration(declaration, self.scope)


def generate_block(block, external_scope):
    generator = BlockGenerator(external_scope)
    for item in block.block_items:
        yield from generator.visit(item)

