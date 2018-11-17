from abc import ABC, abstractmethod
from contextlib import contextmanager

from turingarena.driver.interface.variables import ReferenceDirection
from turingarena.util.visitor import Visitor


class CodeGen(ABC, Visitor):
    __slots__ = []


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
    __slots__ = ["indentation"]

    def __init__(self):
        self.indentation = 0

    @contextmanager
    def indent(self):
        self.indentation += 1
        yield
        self.indentation -= 1

    def generate_to_file(self, interface, file):
        for line in self.generate(interface):
            if line is None:
                print("", file=file)
            else:
                print("    " * self.indentation + line, file=file)

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
            yield from self.visit_MethodPrototype(func)

    def generate_constants_declarations(self, constants):
        if constants:
            yield self.line_comment("Constant declarations")
            for name, value in constants.items():
                yield from self.generate_constant_declaration(name, value)
            yield

    @abstractmethod
    def visit_MethodPrototype(self, m):
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


class StatementDescriptionCodeGen(AbstractExpressionCodeGen):
    def visit_IntermediateNode(self, n):
        pass

    def visit_ReadStatement(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"read {args}"

    def visit_OutputStatement(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"write {args}"

    def visit_CheckpointStatement(self, s):
        return f"checkpoint"

    def visit_CallStatement(self, s):
        method = s.method

        args = ", ".join(self.visit(p) for p in s.arguments)
        if method.has_return_value:
            return_value = f"{self.visit(s.return_value)} = "
        else:
            return_value = ""

        if method.has_callbacks:
            callbacks = " callbacks {...}"
        else:
            callbacks = ""

        return f"call {return_value}{method.name}({args}){callbacks}"

    def visit_ReturnStatement(self, s):
        return f"return {self.visit(s.value)}"

    def visit_ExitStatement(self, s):
        return "exit"

    def visit_BreakStatement(self, s):
        return "break"

    def visit_ForStatement(self, s):
        index = s.index
        return f"for {index.variable.name} to {self.visit(index.range)} " "{...}"

    def visit_LoopStatement(self, s):
        return "loop {...}"

    def visit_IfStatement(self, s):
        if s.else_body is not None:
            body = "{...} else {...}"
        else:
            body = "{...}"
        return f"if {self.visit(s.condition)} {body}"

    def visit_SwitchStatement(self, s):
        return f"switch {self.visit(s.value)} " "{...}"


class SkeletonCodeGen(InterfaceCodeGen, AbstractExpressionCodeGen):
    __slots__ = []

    @abstractmethod
    def visit_ReadStatement(self, s):
        pass

    @abstractmethod
    def visit_OutputStatement(self, s):
        pass

    @abstractmethod
    def visit_CallStatement(self, s):
        pass

    @abstractmethod
    def visit_IfStatement(self, s):
        pass

    @abstractmethod
    def visit_ForStatement(self, s):
        pass

    @abstractmethod
    def visit_LoopStatement(self, s):
        pass

    @abstractmethod
    def visit_SwitchStatement(self, s):
        pass

    @abstractmethod
    def visit_ExitStatement(self, statement):
        pass

    @abstractmethod
    def visit_ReturnStatement(self, statement):
        pass

    @abstractmethod
    def visit_BreakStatement(self, statement):
        pass

    def visit_SequenceNode(self, node):
        for child in node.children:
            yield from self.generate_statement(child)

    @abstractmethod
    def visit_VariableDeclaration(self, d):
        pass

    @abstractmethod
    def visit_VariableAllocation(self, a):
        pass

    def visit_IntermediateNode(self, s):
        # ignore any other node
        return []

    def visit_Step(self, s):
        if s.direction is ReferenceDirection.DOWNWARD:
            # insert an (upward) flush before receiving data downward
            yield from self.generate_flush()
        yield from self.visit_SequenceNode(s)

    def generate_main_block(self, interface):
        yield from self.visit(interface.main_block)

    def generate_statement(self, statement):
        if statement.comment is not None:
            yield self.line_comment(statement.comment)
        else:
            comment = StatementDescriptionCodeGen().visit(statement)
            if comment is not None:
                yield self.line_comment(comment)

        for d in statement.variable_declarations:
            yield from self.visit(d)

        for a in statement.variable_allocations:
            yield from self.visit(a)

        yield from self.visit(statement)

    @abstractmethod
    def generate_flush(self):
        pass


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        yield from ()
