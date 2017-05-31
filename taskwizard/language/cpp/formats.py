class FormatGenerator:

    def generate(self, type):
        return "%d" # TODO: avoids variable definition lookup

        method = getattr(self, "generate_%s" % type.parseinfo.rule)
        return method(type)

    def generate_array_type(self, type):
        return "%d"


generator = FormatGenerator()


def generate_format(type):
    return generator.generate(type)
