import logging
from abc import abstractmethod
from collections import namedtuple

from bidict import frozenbidict

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.variables import Variable
from turingarena.util.visitor import Visitor

logger = logging.getLogger(__name__)


class Expression:
    __slots__ = []

    @staticmethod
    def compile(ast, context):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def reference(self):
        return self.context.statement_context.reference(self)


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

    @property
    def variable(self):
        declared = Variable(
            name=self.variable_name,
            dimensions=self.context.index_count,
        )
        if self.context.declaring:
            return declared
        else:
            referenced = self._get_referenced_variable()
            if referenced is None:  # quirk
                return declared
            return referenced

    def _get_referenced_variable(self):
        variable_mapping = self.context.statement_context.variable_mapping
        return variable_mapping.get(self.variable_name, None)

    def is_reference_to(self, variable):
        return self.variable == variable

    def validate(self):
        if not self.context.declaring and not self._is_declared():
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_NOT_DECLARED,
                self.variable_name,
                parseinfo=self.ast.parseinfo,
            )
        if self.context.declaring and self._is_declared():
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_REUSED,
                self.variable_name,
                parseinfo=self.ast.parseinfo,
            )

    def _is_declared(self):
        return self._get_referenced_variable() is not None


class Subscript(Expression, namedtuple("Subscript", [
    "array",
    "index",
    "context",
])):
    __slots__ = []


def compile_subscript(ast, index_asts, context):
    if index_asts:
        array = compile_subscript(ast, index_asts[:-1], context._replace(
            index_count=context.index_count + 1,
        ))
        index = Expression.compile(index_asts[-1], context._replace(
            declaring=False,
            resolved=True,
            reference=False,
            index_count=0,
        ))
        return Subscript(array, index, context)
    else:
        return VariableReference(ast, context)


def compile_reference_expression(ast, context):
    return compile_subscript(ast, ast.indices, context)


expression_classes = frozenbidict({
    "int_literal": IntLiteralAst,
    "reference_subscript": compile_reference_expression,
    "nested": lambda ast, context: Expression.compile(ast.expression, context),
})


class ExpressionVisitor(Visitor):
    def visit_Expression(self, e):
        raise NotImplementedError

    def visit_Literal(self, e):
        return NotImplemented

    def visit_IntLiteral(self, e):
        return NotImplemented

    def visit_VariableReference(self, e):
        return NotImplemented

    def visit_Subscript(self, e):
        return NotImplemented
