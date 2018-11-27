import logging
from abc import abstractmethod
from collections import namedtuple

from bidict import frozenbidict

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper

logger = logging.getLogger(__name__)


class Expression:
    __slots__ = []

    @staticmethod
    def compile(ast):
        return expression_classes[ast.expression_type](ast, context=None)


class Literal(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass


class IntLiteral(Literal):
    __slots__ = []


class IntLiteralAst(IntLiteral, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)


class IntLiteralSynthetic(
    namedtuple("IntLiteralSynthetic", ["value"]),
    IntLiteral,
):
    __slots__ = []


class VariableReference(Expression, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def variable_name(self):
        return self.ast.variable_name


class Subscript(Expression, namedtuple("Subscript", [
    "array",
    "index",
    "context",
])):
    __slots__ = []


def compile_subscript(ast, index_asts):
    if index_asts:
        array = compile_subscript(ast, index_asts[:-1])
        index = Expression.compile(index_asts[-1])
        return Subscript(array, index, None)
    else:
        return VariableReference(ast, None)


def compile_reference_expression(ast, context):
    return compile_subscript(ast, ast.indices)


expression_classes = frozenbidict({
    "int_literal": IntLiteralAst,
    "reference_subscript": compile_reference_expression,
    "nested": lambda ast, context: Expression.compile(ast.expression),
})
