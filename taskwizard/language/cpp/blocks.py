from taskwizard.language.cpp.formats import generate_format
from taskwizard.language.cpp.utils import indent
from taskwizard.language.cpp.declarations import generate_declarator, generate_declaration
from taskwizard.language.cpp.expressions import generate_expression
from taskwizard.language.cpp.types import generate_base_type


class BlockGenerator:

    def generate(self, block):
        for item in block.block_items:
            yield from self.generate_block_item(item)

    def generate_block_item(self, item):
        method = getattr(self, "generate_%s" % item.parseinfo.rule)
        yield from method(item)

    def generate_for_statement(self, statement):
        yield 'for(int {index} = {start}; {index} <= {end}; {index}++)'.format(
                index=statement.index,
                start=generate_expression(statement.range.start),
                end=generate_expression(statement.range.end)
        ) + " {"
        yield from indent(generate_support_block(statement.block))
        yield "}"


class SupportBlockGenerator(BlockGenerator):

    def generate_local_declaration(self, declaration):
        yield from generate_declaration(declaration)

    def generate_input_statement(self, statement):
        format_string = ''.join(generate_format(v.type) for v in statement.arguments)
        args = ', '.join("&" + generate_expression(v) for v in statement.arguments)

        yield 'scanf("{format}", {args});'.format(format=format_string, args=args)

    def generate_output_statement(self, node):
        format_string = ' '.join(generate_format(v.type) for v in node.arguments) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.arguments)

        yield 'printf("{format}", {args});'.format(format=format_string, args=args)

    def generate_call_statement(self, node):
        if node.return_value is not None:
            return_value = generate_expression(node.return_value) + " = "
        else:
            return_value = ""

        yield "{return_value}{function_name}({parameters});".format(
            return_value=return_value,
            function_name=node.function_name,
            parameters=", ".join(generate_expression(p) for p in node.parameters)
        )


class InterfaceDriverBlockGenerator(BlockGenerator):

    def input_node(self, node):
        format_string = ' '.join(generate_format(v.type) for v in node.variables) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.variables)

        yield 'fprintf(dpipe, "{format}", {args});'.format(format=format_string, args=args)

    def output_node(self, node):
        format_string = ''.join(generate_format(v.type) for v in node.variables)
        args = ', '.join("&" + generate_expression(v) for v in node.variables)

        yield 'fscanf(upipe, "{format}", {args});'.format(format=format_string, args=args)

    def call_node(self, node):
        return []


support_generator = SupportBlockGenerator()

def generate_support_block(block):
    return support_generator.generate(block)
