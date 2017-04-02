from taskwizard.definition import expression


class CodeGenerator:

    def indent(self, lines):
        for line in lines:
            yield "    " + line

    def generate_protocol(self, protocol):
        return self.generate_protocol_steps(protocol.steps)

    def generate_protocol_steps(self, steps):
        for step in steps:
            yield from self.generate_step(step)

    def generate_step(self, step):
        node_type = step.get_node_type()
        method = getattr(self, "generate_%s_node" % node_type)
        yield from method(step)

    def generate_input_node(self, node):
        format_string = ''.join(self.get_format(v) for v in node.variables)
        args = ', '.join("&" + self.generate_expression(v) for v in node.variables)

        yield 'scanf("%s", %s);' % (format_string, args)

    def generate_for_node(self, node):
        yield 'for({index}={start}; {index}<={end}; {index}++)'.format(
                index=node.index,
                start=self.generate_expression(node.range.start),
                end=self.generate_expression(node.range.end)
        ) + " {"
        yield from self.indent(self.generate_protocol_steps(node.steps))
        yield "}"

    def get_format(self, variable):
        return "%d"

    def generate_expression(self, expression):
        expression_type = expression.get_expression_type()
        method = getattr(self, "generate_%s_expression" % expression_type)
        return method(expression)

    def generate_int_literal_expression(self, e):
        return str(e.value)

    def generate_variable_expression(self, e):
        return e.variable_name + ''.join('[' + self.generate_expression(i) + ']' for i in e.indexes)