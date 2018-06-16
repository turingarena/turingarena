from abc import ABC, abstractmethod

from turingarena_impl.interface.statements.statement import AbstractStatement


class CodeGen(ABC):
    __slots__ = []

    def indent_all(self, lines):
        for line in lines:
            yield self.indent(line)

    def indent(self, line):
        if line is None:
            return None
        else:
            return "    " + line


class ExpressionCodeGen(CodeGen):
    __slots__ = []

    def expression(self, e):
        return getattr(self, f"{e.expression_type}_expression")(e)

    def subscript_expression(self, e):
        return f"{self.expression(e.array)}[{self.expression(e.index)}]"

    def reference_expression(self, e):
        return e.variable_name

    def int_literal_expression(self, e):
        return str(e.value)


class StatementCodeGen(CodeGen):
    __slots__ = []

    def statement(self, statement):
        method_name = f"{statement.statement_type}_statement"
        yield from getattr(self, method_name)(statement)

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


class InterfaceCodeGen(CodeGen):
    __slots__ = []

    def generate_to_file(self, interface, file):
        for line in self.generate(interface):
            if line is None:
                print("", file=file)
            else:
                print(line, file=file)

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

    @abstractmethod
    def line_comment(self, comment):
        pass


class StatementDescriptionCodeGen(StatementCodeGen, ExpressionCodeGen):
    def read_statement(self, read_statement):
        args = ", ".join(self.expression(a) for a in read_statement.arguments)
        yield f"read {args};"

    def write_statement(self, write_statement):
        args = ", ".join(self.expression(a) for a in write_statement.arguments)
        yield f"write {args};"

    def checkpoint_statement(self, checkpoint_statement):
        yield f"checkpoint;"

    def call_statement(self, call_statement):
        method = call_statement.method

        args = ", ".join(self.expression(p) for p in call_statement.arguments)
        if method.has_return_value:
            return_value = f"{self.expression(call_statement.return_value)} = "
        else:
            return_value = ""

        if method.has_callbacks:
            callbacks = " callbacks {...}"
        else:
            callbacks = ";"

        yield f"call {return_value}{method.name}({args}){callbacks}"

    def return_statement(self, return_statement):
        yield f"return {self.expression(return_statement.value)};"

    def exit_statement(self, exit_statement):
        yield "exit;"

    def break_statement(self, break_statement):
        yield "break;"

    def for_statement(self, for_statement):
        index = for_statement.index
        yield f"for {index.variable.name} to {self.expression(index.range)} " "{...}"

    def loop_statement(self, loop_statement):
        yield "loop {...}"

    def if_statement(self, if_statement):
        if if_statement.else_body is not None:
            body = "{...} else {...}"
        else:
            body = "{...}"
        yield f"if {self.expression(if_statement.condition)} {body}"

    def switch_statement(self, switch_statement):
        yield f"switch {self.expression(switch_statement.value)} " "{...}"


class SkeletonCodeGen(InterfaceCodeGen, StatementCodeGen, ExpressionCodeGen):
    __slots__ = []

    @property
    def statement_comment_generator(self):
        return self._statement_comment_generator()

    def _statement_comment_generator(self):
        return StatementDescriptionCodeGen()

    def generate_main_block(self, interface):
        yield from self.block_content(interface.main_block)

    def block(self, block):
        yield from self.indent_all(self.block_content(block))

    def block_content(self, block):
        for statement in block.synthetic_statements:
            yield
            if statement.comment is not None:
                yield self.line_comment(statement.comment)
            else:
                for comment in self.statement_comment_generator.statement(statement):
                    yield self.line_comment(comment)
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

        yield from self.statement(statement)

    @abstractmethod
    def generate_variable_allocation(self, variables, indexes, size):
        pass

    @abstractmethod
    def generate_variable_declaration(self, declared_variable):
        pass

    @abstractmethod
    def generate_flush(self):
        pass


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        yield from ()
