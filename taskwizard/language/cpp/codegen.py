class ExpressionGenerator:

    def generate(self, expression):
        expression_type = expression.get_expression_type()
        method = getattr(self, "%s_expression" % expression_type)
        return method(expression)

    def int_literal_expression(self, e):
        return str(e.value)

    def variable_expression(self, e):
        return e.variable_name + ''.join('[' + self.generate(i) + ']' for i in e.indexes)


class ProtocolGenerator:

    def generate_steps(self, steps):
        for step in steps:
            yield from self.generate_step(step)

    def generate_step(self, step):
        node_type = step.get_node_type()
        method = getattr(self, "%s_node" % node_type)
        yield from method(step)

    def for_node(self, node):
        yield 'for({index}={start}; {index}<={end}; {index}++)'.format(
                index=node.index,
                start=generate_expression(node.range.start),
                end=generate_expression(node.range.end)
        ) + " {"
        yield from indent(self.generate_steps(node.steps))
        yield "}"

    def get_format(self, variable):
        return "%d"


class InterfaceProtocolGenerator(ProtocolGenerator):

    def input_node(self, node):
        format_string = ''.join(self.get_format(v) for v in node.variables)
        args = ', '.join("&" + generate_expression(v) for v in node.variables)

        yield 'scanf("{format}", {args});'.format(format=format_string, args=args)

    def output_node(self, node):
        format_string = ' '.join(self.get_format(v) for v in node.variables) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.variables)

        yield 'printf("{format}", {args});'.format(format=format_string, args=args)

    def call_node(self, node):
        if node.return_value is not None:
            return_value = generate_expression(node.return_value) + " = "
        else:
            return_value = ""

        yield "{return_value}{function_name}({parameters});".format(
            return_value=return_value,
            function_name=node.function_name,
            parameters=", ".join(generate_expression(p) for p in node.parameters)
        )


class InterfaceDriverProtocolGenerator(ProtocolGenerator):

    def input_node(self, node):
        format_string = ' '.join(self.get_format(v) for v in node.variables) + r'\n'
        args = ', '.join(generate_expression(v) for v in node.variables)

        yield 'fprintf(dpipe, "{format}", {args});'.format(format=format_string, args=args)

    def output_node(self, node):
        format_string = ''.join(self.get_format(v) for v in node.variables)
        args = ', '.join("&" + generate_expression(v) for v in node.variables)

        yield 'fscanf(upipe, "{format}", {args});'.format(format=format_string, args=args)

    def call_node(self, node):
        return []

class CodeGenerator:

    def generate_interface_support(self, interface):
        for variable in interface.variables.values():
            yield from self.generate_variable_declaration(variable);

        yield ""

        for protocol in interface.protocols.values():
            yield from self.generate_interface_protocol(protocol)

    def generate_interface_driver_support(self, interface):
        for variable in interface.variables.values():
            yield from self.generate_variable_declaration(variable);

        yield ""

        for protocol in interface.protocols.values():
            yield from self.generate_interface_driver_protocol(interface, protocol)

    def generate_variable_declaration(self, variable):
        yield "{type} {name}{dimensions};".format(
            type=variable.type,
            name=variable.name,
            dimensions=''.join('[1+' + generate_expression(d.end) + ']' for d in variable.array_dimensions)
        )

    def generate_interface_protocol(self, protocol):
        yield "void accept_{name}()".format(name=protocol.name) + " {"
        yield from indent(InterfaceProtocolGenerator().generate_steps(protocol.steps))
        yield "}"

    def generate_interface_driver_protocol(self, interface, protocol):
        yield "void send_{interface_name}_{name}(int process_id)".format(interface_name=interface.name,name=protocol.name) + " {"
        yield "    FILE* dpipe = get_downward_pipe(process_id);"
        yield "    FILE* upipe = get_upward_pipe(process_id);"
        yield ""
        yield from indent(InterfaceDriverProtocolGenerator().generate_steps(protocol.steps))
        yield "}"


def generate_expression(expression):
    return ExpressionGenerator().generate(expression)


def indent(lines):
    for line in lines:
        yield "    " + line
