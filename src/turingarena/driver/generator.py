from abc import ABC, abstractmethod
from contextlib import contextmanager

from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.nodes import Print, IntLiteral
from turingarena.driver.interface.variables import ReferenceDirection
from turingarena.util.visitor import Visitor


class CodeGen(ABC, Visitor):
    __slots__ = []


class AbstractExpressionCodeGen(CodeGen):
    __slots__ = []

    def visit_Subscript(self, e):
        return f"{self.visit(e.array)}[{self.visit(e.index)}]"

    def visit_Variable(self, e):
        return e.name

    def visit_IntLiteral(self, e):
        return str(e.value)


class LineCollector:
    def __init__(self):
        self._lines = []

    def indented_lines(self):
        for indentation, l in self._lines:
            if l is None:
                yield "\n"
            else:
                yield "    " * indentation + l + "\n"

    def add_line(self, indentation, line):
        self._lines.append((indentation, line))

    def _inline_chunks(self):
        for i, (indentation, l) in enumerate(self._lines):
            if i > 0:
                yield "\n"
                if l is not None:
                    yield "    " * indentation
            if l is not None:
                yield l

    def __iter__(self):
        return iter(self.indented_lines())

    def as_inline(self):
        return "".join(self._inline_chunks())

    def as_block(self):
        return "".join(self.indented_lines())


class LinesGenerator:
    __slots__ = ["indentation", "collector"]

    def __init__(self):
        self.indentation = 0
        self.collector = None

    @contextmanager
    def collect_lines(self):
        old_collector = self.collector
        self.collector = collector = LineCollector()
        yield collector
        assert self.collector is collector
        self.collector = old_collector

    @contextmanager
    def indent(self):
        self.indentation += 1
        yield
        self.indentation -= 1

    def line(self, line=None):
        self.collector.add_line(self.indentation, line)

    @abstractmethod
    def _on_generate(self, *args, **kwargs):
        pass


class InterfaceCodeGen(CodeGen, LinesGenerator):
    __slots__ = []

    def generate_to_file(self, interface, file):
        with self.collect_lines() as lines:
            self.generate(interface)
        file.write(lines.as_block())

    def generate(self, interface):
        self.generate_header(interface)
        self.generate_constants_declarations(interface)
        self.generate_method_declarations(interface)
        self.generate_main_block(interface)
        self.generate_footer(interface)

    def generate_header(self, interface):
        pass

    def generate_footer(self, interface):
        pass

    def generate_method_declarations(self, interface):
        for func in interface.methods:
            self.visit_MethodPrototype(func)

    def generate_constants_declarations(self, interface):
        for c in interface.constants:
            self.visit(c)

    @abstractmethod
    def visit_MethodPrototype(self, m):
        pass

    @abstractmethod
    def visit_ConstantDeclaration(self, m):
        pass

    @abstractmethod
    def generate_main_block(self, interface):
        pass

    @abstractmethod
    def line_comment(self, comment):
        pass


class StatementDescriptionCodeGen(AbstractExpressionCodeGen):
    def visit_object(self, n):
        pass

    def visit_Read(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"read {args}"

    def visit_Print(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"write {args}"

    def visit_Checkpoint(self, s):
        return f"checkpoint"

    def visit_Call(self, s):
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

    def visit_Return(self, s):
        return f"return {self.visit(s.value)}"

    def visit_Exit(self, s):
        return "exit"

    def visit_Break(self, s):
        return "break"

    def visit_For(self, s):
        index = s.index
        return f"for {index.variable.name} to {self.visit(index.range)} " "{...}"

    def visit_Loop(self, s):
        return "loop {...}"

    def visit_If(self, s):
        if s.else_body is not None:
            body = "{...} else {...}"
        else:
            body = "{...}"
        return f"if {self.visit(s.condition)} {body}"

    def visit_Switch(self, s):
        return f"switch {self.visit(s.value)} " "{...}"


class SkeletonCodeGen(InterfaceCodeGen, AbstractExpressionCodeGen):
    __slots__ = []

    def visit_Write(self, s):
        return self.visit(
            Print(s.arguments)
        )

    def visit_Checkpoint(self, s):
        return self.visit(
            Print([IntLiteral(0)])
        )

    @abstractmethod
    def visit_Read(self, s):
        pass

    @abstractmethod
    def visit_Print(self, s):
        pass

    @abstractmethod
    def visit_Call(self, s):
        pass

    @abstractmethod
    def visit_If(self, s):
        pass

    @abstractmethod
    def visit_For(self, s):
        pass

    @abstractmethod
    def visit_Loop(self, s):
        pass

    @abstractmethod
    def visit_Switch(self, s):
        pass

    @abstractmethod
    def visit_Exit(self, statement):
        pass

    @abstractmethod
    def visit_Return(self, statement):
        pass

    @abstractmethod
    def visit_Break(self, statement):
        pass

    def visit_SequenceNode(self, node):
        for child in node.children:
            self.generate_statement(child)

    @abstractmethod
    def visit_VariableDeclaration(self, d):
        pass

    @abstractmethod
    def visit_ReferenceAllocation(self, a):
        pass

    def visit_object(self, s):
        # ignore any other node
        return []

    def visit_Step(self, s):
        if s.direction is ReferenceDirection.DOWNWARD:
            # insert an (upward) flush before receiving data downward
            self.generate_flush()
        self.visit_SequenceNode(s)

    def visit_PrintNoCallbacks(self, s):
        return self.visit(
            Print([IntLiteral(0), IntLiteral(0)])
        )

    def visit_PrintCallbackRequest(self, s):
        return self.visit(
            Print([IntLiteral(1), IntLiteral(s.index)])
        )

    def generate_main_block(self, interface):
        self.visit(interface.main_block)

    def generate_statement(self, statement):
        analyzer = TreeAnalyzer()

        comment = analyzer.comment(statement)
        if comment is not None:
            comment = StatementDescriptionCodeGen().visit(statement)
        if comment is not None:
            self.line_comment(comment)

        for d in analyzer.variable_declarations(statement):
            self.visit(d)

        for a in analyzer.reference_allocations(statement):
            self.visit(a)

        self.visit(statement)

    @abstractmethod
    def generate_flush(self):
        pass


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        pass
