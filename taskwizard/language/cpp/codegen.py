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

    def __init__(self, interface, protocol):
        self.interface = interface
        self.protocol = protocol

        self.arrays_to_allocate = list(interface.get_arrays_to_allocate(protocol))

    def generate_steps(self, steps):
        for step in steps:
            yield from self.generate_step(step)

    def generate_step(self, step):
        node_type = step.get_node_type()
        method = getattr(self, "%s_node" % node_type)
        yield from method(step)

    def for_node(self, node):
        for n, var, indexes in self.arrays_to_allocate:
            if not n == node: continue
            yield "{name} = new {type}[{size}+1];".format(
                name=var.name,
                type=var.type,
                size=generate_expression(var.array_dimensions[0].end)
            )

        yield 'for(int {index} = {start}; {index} <= {end}; {index}++)'.format(
                index=node.index.name,
                start=generate_expression(node.index.range.start),
                end=generate_expression(node.index.range.end)
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
        yield "#include <cstdio>"

        yield ""

        for variable in interface.variables.values():
            yield from self.generate_variable_declaration(variable);

        yield ""

        for function in interface.functions.values():
            yield from self.generate_function_declaration(function);

        yield ""

        yield from self.generate_main_interface_protocol(interface)

        for protocol in interface.named_protocols.values():
            yield from self.generate_interface_protocol(interface, protocol)

    def generate_interface_driver_support(self, interface):
        for variable in interface.variables.values():
            yield from self.generate_variable_declaration(variable);

        yield ""

        yield from self.generate_interface_driver_protocol(interface, interface.main_protocol)

    def generate_variable_declaration(self, variable):
        yield self.format_variable(variable) + ";"

    def format_variable(self, variable):
        return "{type} {stars}{name}".format(
            type=variable.type,
            name=variable.name,
            stars='*' * len(variable.array_dimensions)
        )

    def generate_function_declaration(self, function):
        yield "{return_type} {name}({arguments});".format(
            return_type=function.return_type,
            name=function.name,
            arguments=', '.join(self.format_variable(p) for p in function.parameters.values())
        )

    def generate_main_interface_protocol(self, interface):
        protocol = interface.main_protocol

        yield "int main() {"
        yield from indent(InterfaceProtocolGenerator(interface, protocol).generate_steps(protocol.steps))
        yield "}"

    def generate_interface_driver_protocol(self, interface, protocol):
        yield ""


def generate_expression(expression):
    return ExpressionGenerator().generate(expression)


def indent(lines):
    for line in lines:
        yield "    " + line
