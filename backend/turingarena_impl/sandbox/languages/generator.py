from abc import ABC, abstractmethod


class CodeGen(ABC):
    __slots__ = []

    def generate_to_file(self, data, file):
        for line in self.generate(data):
            if line is None:
                print("", file=file)
            else:
                print(line, file=file)

    def indent_all(self, lines):
        for line in lines:
            yield self.indent(line)

    def indent(self, line):
        if line is None:
            return None
        else:
            return "    " + line

    @abstractmethod
    def generate(self, data):
        yield from None


class InterfaceCodeGen(CodeGen):
    __slots__ = []

    def generate(self, interface):
        yield from self.generate_header(interface)
        yield from self.generate_method_declarations(interface)
        yield from self.generate_main_block(interface)
        yield from self.generate_footer(interface)

    def generate_header(self, interface):
        yield from ()

    def generate_footer(self, interface):
        yield from ()

    def generate_method_declarations(self, interface):
        for func in interface.methods:
            yield from self.generate_method_declaration(func)

    @abstractmethod
    def generate_method_declaration(self, method_declaration):
        pass

    @abstractmethod
    def generate_main_block(self, interface):
        pass


class SkeletonCodeGen(InterfaceCodeGen):
    __slots__ = []

    def generate_main_block(self, interface):
        yield from self.block_content(interface.main_block, indent=False)

    def block_content(self, block, indent=True):
        for statement in block.synthetic_statements:
            if indent:
                yield from self.indent_all(self.generate_statement(statement))
            else:
                yield from self.generate_statement(statement)

    def generate_statement(self, statement):
        for var in statement.variables_to_declare:
            yield from self.generate_variable_declaration(var)

        for allocation in statement.variables_to_allocate:
            variable = allocation.reference.variable
            indexes = statement.context.index_variables[-allocation.reference.index_count:]
            yield from self.generate_variable_allocation(variable, indexes, allocation.size)

        if statement.needs_flush:
            yield from self.generate_flush()

        method_name = f"{statement.statement_type}_statement"
        yield from getattr(self, method_name)(statement)

    @abstractmethod
    def generate_variable_allocation(self, variables, indexes, size):
        pass

    @abstractmethod
    def generate_variable_declaration(self, declared_variable):
        pass

    @abstractmethod
    def generate_flush(self):
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

    def subscript_expression(self, e):
        return f"{self.expression(e.array)}[{self.expression(e.index)}]"

    def reference_expression(self, e):
        return e.variable_name

    def int_literal_expression(self, e):
        return str(e.value)


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        yield from ()
