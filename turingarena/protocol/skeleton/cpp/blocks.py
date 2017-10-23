from turingarena.protocol.codegen.utils import indent_all
from turingarena.protocol.visitor import accept_statement
from turingarena.protocol.skeleton.cpp.declarations import build_declaration
from turingarena.protocol.skeleton.cpp.expressions import generate_expression
from turingarena.protocol.skeleton.cpp.types import build_type_expression


def generate_format(expr):
    return {
        "int": "%d",
        "int64": "%lld",
    }[expr.type.base]


class BlockItemGenerator:
    def visit_for_statement(self, statement):
        yield 'for(int {index} = 0; {index} < {end}; {index}++)'.format(
            index=statement.index.declarator.name,
            end=generate_expression(statement.index.range)
        ) + " {"
        yield from indent_all(generate_block(statement.body))
        yield "}"

    def visit_if_statement(self, statement):
        yield 'if( {condition} )'.format( condition = generate_expression(statement.condition)
        ) + " {"
        yield from indent_all(generate_block(statement.then_body))
        yield "}"
        if  hasattr(statement,'else_body'):
            yield "else  {"
            yield from indent_all(generate_block(statement.else_body))
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

    def visit_exit_statement(self, statement):
        yield 'exit(1);'

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
                type=build_type_expression(argument.type.item_type),
                size=generate_expression(statement.size),
            )

    def visit_return_statement(self, stmt):
        yield "return {expr};".format(expr=generate_expression(stmt.value))

    def visit_var_statement(self, declaration):
        yield build_declaration(declaration)


def generate_block(block):
    for statement in block.statements:
        yield from accept_statement(statement, visitor=BlockItemGenerator())
