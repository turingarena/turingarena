from collections import namedtuple
from abc import ABC, abstractmethod


class CodeGen(ABC, namedtuple("CodeGen", ["interface"])):
    __slots__ = []

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
        yield from self.generate_footer()

    def block_content(self, block, indent=True):
        for statement in block.statements:
            if indent:
                yield from self.indent_all(self.generate_statement(statement))
            else:
                yield from self.generate_statement(statement)

    def generate_statement(self, statement):
        for var in statement.variables_to_declare:
            yield from self.generate_variable_declaration(var)
        for var in statement.variables_to_allocate:
            yield from self.generate_variable_allocation(var)
        if statement.needs_flush:
            yield from self.generate_flush()

        method_name = f"{statement.statement_type}_statement"
        yield from getattr(self, method_name)(statement)

    def generate_header(self):
        yield from ()

    def generate_footer(self):
        yield from ()

    def generate_functions(self):
        for func in self.interface.functions:
            yield from self.generate_function_declaration(func)

    def generate_main_block(self):
        yield from self.block_content(self.interface.main, indent=False)

    @abstractmethod
    def generate_variable_allocation(self, allocated_variable):
        pass

    @abstractmethod
    def generate_variable_declaration(self, declared_variable):
        pass

    @abstractmethod
    def generate_function_declaration(self, function_declaration):
        pass

    @abstractmethod
    def generate_flush(self):
        pass

    @abstractmethod
    def callback_statement(self, callback_statement):
        pass

    @abstractmethod
    def read_statement(self, read_statement):
        pass

    @abstractmethod
    def write_statement(self, write_statement):
        pass

    @abstractmethod
    def checkpoint_statement(self, checkpoint_statement):
        pass

    @abstractmethod
    def break_statement(self, break_statement):
        pass

    @abstractmethod
    def exit_statement(self, exit_statement):
        pass

    @abstractmethod
    def return_statement(self, return_statement):
        pass

    @abstractmethod
    def call_statement(self, call_statement):
        pass

    @abstractmethod
    def if_statement(self, if_statement):
        pass

    @abstractmethod
    def switch_statement(self, switch_statement):
        pass

    @abstractmethod
    def for_statement(self, for_statement):
        pass

    @abstractmethod
    def loop_statement(self, loop_statement):
        pass

    def expression(self, e):
        return getattr(self, f"{e.expression_type}_expression")(e)

    def reference_expression(self, e):
        subscripts = "".join(f"[{self.expression(index)}]" for index in e.indices)
        return f"{e.variable_name}{subscripts}"

    def int_literal_expression(self, e):
        return str(e.value)

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
