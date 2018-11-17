from abc import ABC, abstractmethod

from turingarena.driver.interface.expressions import IntLiteralExpressionSynthetic
from turingarena.driver.interface.statements.statement import SyntheticStatement, Statement, AbstractStatement
from turingarena.driver.visitors import StatementVisitor
from turingarena.util.visitor import Visitor


class CodeGen(ABC, Visitor):
    __slots__ = []

    def indent_all(self, lines):
        for line in lines:
            yield self.indent(line)

    def indent(self, line):
        if line is None:
            return None
        else:
            return "    " + line


class AbstractExpressionCodeGen(CodeGen):
    __slots__ = []

    def expression(self, e):
        return self.visit(e)

    def visit_SubscriptExpression(self, e):
        return f"{self.visit(e.array)}[{self.visit(e.index)}]"

    def visit_VariableReferenceExpression(self, e):
        return e.variable_name

    def visit_IntLiteralExpression(self, e):
        return str(e.value)


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
        yield from self.generate_constants_declarations(interface.constants)
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

    def generate_constants_declarations(self, constants):
        if constants:
            yield self.line_comment("Constant declarations")
            for name, value in constants.items():
                yield from self.generate_constant_declaration(name, value)
            yield

    @abstractmethod
    def generate_method_declaration(self, method_declaration):
        pass

    @abstractmethod
    def generate_constant_declaration(self, name, value):
        pass

    @abstractmethod
    def generate_main_block(self, interface):
        pass

    @abstractmethod
    def line_comment(self, comment):
        pass


class StatementDescriptionCodeGen(StatementVisitor, AbstractExpressionCodeGen):
    def read_statement(self, read_statement):
        args = ", ".join(self.expression(a) for a in read_statement.arguments)
        yield f"read {args}"

    def write_statement(self, write_statement):
        args = ", ".join(self.expression(a) for a in write_statement.arguments)
        yield f"write {args}"

    def checkpoint_statement(self, checkpoint_statement):
        yield f"checkpoint"

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
            callbacks = ""

        yield f"call {return_value}{method.name}({args}){callbacks}"

    def return_statement(self, return_statement):
        yield f"return {self.expression(return_statement.value)}"

    def exit_statement(self, exit_statement):
        yield "exit"

    def break_statement(self, break_statement):
        yield "break"

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


class SkeletonCodeGen(InterfaceCodeGen, StatementVisitor, AbstractExpressionCodeGen):
    __slots__ = []

    @property
    def statement_comment_generator(self):
        return self._statement_comment_generator()

    def _statement_comment_generator(self):
        return StatementDescriptionCodeGen()

    def generate_main_block(self, interface):
        yield from self.block_content(interface.main_block)

    def block(self, block):
        yield
        yield from self.indent_all(self.block_content(block))
        yield

    def block_content(self, block):
        for i, node in enumerate(block.flat_inner_nodes):
            if i > 0:
                yield
            yield from self.generate_statement(node)

    def generate_statement(self, statement):
        if statement.comment is not None:
            yield self.line_comment(statement.comment)
        else:
            if isinstance(statement, Statement):
                for comment in self.statement_comment_generator.statement(statement):
                    yield self.line_comment(comment)

        for var in statement.variables_to_declare:
            yield from self.generate_variable_declaration(var)

        for allocation in statement.variables_to_allocate:
            variable = allocation.reference.variable
            indexes = statement.context.index_variables[-allocation.reference.index_count:]
            yield from self.generate_variable_allocation(variable, indexes, allocation.size)

        if statement.needs_flush:
            yield from self.generate_flush()

        if isinstance(statement, AbstractStatement):
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

    def checkpoint_statement(self, checkpoint_statement):
        return self.write_statement(SyntheticStatement("write", None, arguments=[
            IntLiteralExpressionSynthetic(value=0),
        ]))


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        yield from ()
