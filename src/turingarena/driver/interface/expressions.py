import logging
from abc import abstractmethod
from collections import namedtuple

logger = logging.getLogger(__name__)


class ExpressionCompiler:
    __slots__ = []

    def compile(self, ast):
        return getattr(self, f"compile_{ast.expression_type}")(ast)

    def compile_int_literal(self, ast):
        return IntLiteralAst(ast)

    def compile_reference_subscript(self, ast):
        return self.compile_subscript(ast, ast.indices)

    def compile_subscript(self, ast, index_asts):
        if index_asts:
            array = self.compile_subscript(ast, index_asts[:-1])
            index = Expression.compile(index_asts[-1])
            return Subscript(array, index)
        else:
            return VariableReference(ast)


class Expression:
    __slots__ = []

    @staticmethod
    def compile(ast):
        return ExpressionCompiler().compile(ast)


class Literal(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass


class IntLiteral(Literal):
    __slots__ = []


class IntLiteralAst(namedtuple("IntLiteralAst", ["ast"]), IntLiteral):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)


class IntLiteralSynthetic(
    namedtuple("IntLiteralSynthetic", ["value"]),
    IntLiteral,
):
    __slots__ = []


class VariableReference(namedtuple("VariableReference", ["ast"]), Expression):
    __slots__ = []

    @property
    def variable_name(self):
        return self.ast.variable_name


class Subscript(Expression, namedtuple("Subscript", [
    "array",
    "index",
])):
    __slots__ = []
