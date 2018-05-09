class CodeGen:
    __slots__ = ["interface"]

    def __init__(self, interface):
        self.interface = interface

    def write_to_file(self, file):
        for line in self.generate():
            if line is None:
                print("", file=file)
            else:
                print(line, file=file)

    def generate(self):
        yield from self.generate_header()
        yield from self.generate_functions()
        yield from self.generate_main_block()

    def block_content(self, block, indent=True):
        for statement in block.statements:
            if indent:
                yield from self.indent_all(self.generate_statement(statement))
            else:
                yield from self.generate_statement(statement)

    def generate_statement(self, stmt):
        for var in stmt.variables_to_declare:
            yield from self.generate_variable_declaration(var)
        for var in stmt.variables_to_allocate:
            yield from self.generate_variable_allocation(var)

        try:
            method_name = f"{stmt.statement_type}_statement"
            yield from getattr(self, method_name)(stmt)
        except NotImplementedError:
            yield from self.any_statement(stmt)

    def generate_header(self):
        return []

    def generate_functions(self):
        for func in self.interface.functions:
            yield from self.generate_function_declaration(func)

    def generate_variable_allocation(self, var):
        raise NotImplementedError

    def generate_variable_declaration(self, var):
        raise NotImplementedError

    def generate_function_declaration(self, s):
        raise NotImplementedError

    def generate_main_block(self):
        yield from self.block_content(self.interface.main, indent=False)

    def callback_statement(self, s):
        raise NotImplementedError

    def read_statement(self, s):
        raise NotImplementedError

    def write_statement(self, s):
        raise NotImplementedError

    def checkpoint_statement(self, s):
        raise NotImplementedError

    def break_statement(self, s):
        raise NotImplementedError

    def exit_statement(self, s):
        raise NotImplementedError

    def return_statement(self, s):
        raise NotImplementedError

    def call_statement(self, s):
        raise NotImplementedError

    def if_statement(self, s):
        raise NotImplementedError

    def switch_statement(self, s):
        raise NotImplementedError

    def for_statement(self, s):
        raise NotImplementedError

    def loop_statement(self, s):
        raise NotImplementedError

    def any_statement(self, s):
        raise NotImplementedError

    def expression(self, e):
        return getattr(self, f"{e.expression_type}_expression")(e)

    def reference_expression(self, e):
        subscripts = "".join(f"[{self.expression(index)}]" for index in e.indices)
        return f"{e.variable_name}{subscripts}"

    @staticmethod
    def indent_all(lines):
        for line in lines:
            yield CodeGen.indent(line)

    @staticmethod
    def indent(line):
        if line is None:
            return None
        else:
            return "    " + line
