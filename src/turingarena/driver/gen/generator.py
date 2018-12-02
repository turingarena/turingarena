import logging
from abc import ABC, abstractmethod

from turingarena.driver.common.description import TreeDumper
from turingarena.driver.common.expressions import AbstractExpressionCodeGen
from turingarena.driver.common.genutils import LinesGenerator
from turingarena.driver.gen.preprocess import SkeletonPreprocessor
from turingarena.driver.gen.template import interface_template


class InterfaceCodeGen(ABC, LinesGenerator, AbstractExpressionCodeGen):
    __slots__ = []

    def generate_to_file(self, interface, file):
        with self.collect_lines() as lines:
            interface = SkeletonPreprocessor.create().transform(interface)
            logging.debug(f"preprocessed interface: {TreeDumper().dump(interface)}")
            self.visit(interface)

        logging.debug(f"generated code: {lines.as_inline()}")

        file.write(lines.as_block())

    def generate_template_to_file(self, interface, descriptions, file):
        with self.collect_lines() as lines:
            self.visit(interface_template(interface, descriptions))

        logging.debug(f"generated template: {lines.as_inline()}")

        file.write(lines.as_block())

    def visit_Block(self, n):
        for child in n.children:
            self.visit(child)

    @abstractmethod
    def visit_Interface(self, n):
        pass

    @abstractmethod
    def visit_Constant(self, n):
        pass

    @abstractmethod
    def visit_Comment(self, n):
        pass

    @abstractmethod
    def visit_Read(self, n):
        pass

    @abstractmethod
    def visit_Print(self, n):
        pass

    @abstractmethod
    def visit_Call(self, n):
        pass

    @abstractmethod
    def visit_If(self, n):
        pass

    @abstractmethod
    def visit_For(self, n):
        pass

    @abstractmethod
    def visit_Loop(self, n):
        pass

    @abstractmethod
    def visit_Switch(self, n):
        pass

    @abstractmethod
    def visit_Exit(self, n):
        pass

    @abstractmethod
    def visit_Return(self, n):
        pass

    @abstractmethod
    def visit_Break(self, n):
        pass

    @abstractmethod
    def visit_VariableDeclaration(self, n):
        pass

    @abstractmethod
    def visit_Alloc(self, n):
        pass

    @abstractmethod
    def visit_Flush(self, n):
        pass

    def visit_object(self, n):
        # ignore any other node
        return []
