from turingarena.interfaces.codegen.utils import indent_all
from turingarena.interfaces.supportgen.cpp.declarations import build_declaration
from turingarena.interfaces.supportgen.cpp.expressions import generate_expression
from turingarena.interfaces.supportgen.cpp.types import generate_base_type


def generate_format(expr):
    return {
        "int": "%d",
        "int64": "%lld",
    }[expr.type.base]


class BlockItemGenerator:
    def visit_for_statement(self, statement):
        yield 'for(int {index} = {start}; {index} <= {end}; {index}++)'.format(
            index=statement.index.declarator.name,
            start=generate_expression(statement.index.range.start),
            end=generate_expression(statement.index.range.end)
        ) + " {"
        yield from indent_all(generate_block(statement.body))
        yield "}"

    def visit_input_statement(self, statement):
        format_string = ''.join(generate_format(v) for v in statement.arguments)
        args = ', '.join("&" + generate_expression(v) for v in statement.arguments)

        yield 'scanf("{format}", {args});'.format(format=format_string, args=args)

    def visit_output_statement(self, node):
        format_string = ' '.join(generate_format(v) for v in node.arguments) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.arguments)

        yield 'printf("{format}", {args});'.format(format=format_string, args=args)

    def visit_flush_statement(self, statement):
        yield 'fflush(stdout);'

    def visit_call_statement(self, statement):
        if statement.return_value is not None:
            return_value = generate_expression(statement.return_value) + " = "
        else:
            return_value = ""

        yield "{return_value}{function_name}({parameters});".format(
            return_value=return_value,
            function_name=statement.function_name,
            parameters=", ".join(generate_expression(p) for p in statement.parameters)
        )
        interface = statement.outer_block.outer_declaration.interface
        if len(interface.callback_declarations) > 0:
            yield r"""printf("return\n");""".format(statement.function_name)

    def visit_alloc_statement(self, statement):
        for argument in statement.arguments:
            yield "{var} = new {type}[{size}];".format(
                var=generate_expression(argument),
                type=generate_base_type(argument.type),
                size="1 + " + generate_expression(statement.range.end),
            )

    def visit_return_statement(self, stmt):
        yield "return {expr};".format(expr=generate_expression(stmt.value))

    def visit_variable_declaration(self, declaration):
        yield build_declaration(declaration)


def generate_block(block):
    for item in block.block_items:
        yield from item.accept(BlockItemGenerator())
