class ProtocolSupportGenerator:

    def generate(self, protocol):
        return self.generate_steps(protocol.steps)

    def generate_steps(self, steps):
        for step in steps:
            yield from self.generate_step(step)

    def generate_step(self, step):
        node_type = step.get_node_type()
        method = getattr(self, "generate_%s" % node_type)
        yield from method(step)

    def generate_input(self, node):
        format_string = ''.join(self.get_format(v) for v in node.variables)
        args = ', '.join("&" + self.get_reference(v) for v in node.variables)

        yield 'scanf("%s", %s);' % (format_string, args)

    def get_format(self, variable):
        return "%d"

    def get_reference(self, variable):
        return variable.variable_reference
