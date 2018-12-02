import logging
from abc import ABC, abstractmethod

from turingarena.driver.common.description import TreeDumper
from turingarena.driver.common.expressions import AbstractExpressionCodeGen
from turingarena.driver.common.genutils import LinesGenerator
from turingarena.driver.gen.preprocess import TreePreprocessor
from turingarena.util.visitor import Visitor


class CodeGen(ABC, Visitor):
    __slots__ = []


class InterfaceCodeGen(CodeGen, LinesGenerator):
    __slots__ = []

    def generate_to_file(self, interface, file):
        with self.collect_lines() as lines:
            self.generate(interface)

        logging.debug(f"generated code: {lines.as_inline()}")

        file.write(lines.as_block())

    def generate(self, interface):
        interface = TreePreprocessor.create().transform(interface)

        logging.debug(f"preprocessed interface: {TreeDumper().dump(interface)}")

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
            self.method_declaration(func)

    def generate_constants_declarations(self, interface):
        for c in interface.constants:
            self.visit(c)

    @abstractmethod
    def method_declaration(self, m):
        pass

    @abstractmethod
    def visit_Constant(self, m):
        pass

    @abstractmethod
    def generate_main_block(self, interface):
        pass

    @abstractmethod
    def line_comment(self, comment):
        pass


class SkeletonCodeGen(InterfaceCodeGen, AbstractExpressionCodeGen):
    __slots__ = []

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

    def visit_Block(self, node):
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

    def visit_Comment(self, s):
        self.line_comment(s.text)

    def generate_main_block(self, interface):
        self.visit(interface.main_block)

    def generate_statement(self, statement):
        self.visit(statement)

    @abstractmethod
    def visit_Flush(self, n):
        pass


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        pass
