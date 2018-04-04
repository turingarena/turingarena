from abc import abstractmethod
from bidict import frozenbidict

from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena.interface.type_expressions import ScalarType, ArrayType


class Expression(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def compile(ast, context):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def expression_type(self):
        return expression_classes.inv[self.__class__]

    @property
    @abstractmethod
    def value_type(self):
        pass

    def evaluate_in(self, context):
        return self.do_evaluate(context)

    @abstractmethod
    def do_evaluate(self, context):
        pass

    @property
    @abstractmethod
    def canonical_form(self):
        pass

    def validate(self):
        return []


class LiteralExpression(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass

    def do_evaluate(self, context):
        return ConstantReference(
            value_type=self.value_type,
            value=self.value,
        )


class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @property
    def canonical_form(self):
        return self.value

    @property
    def value(self):
        return int(self.ast.int_literal)

    @property
    def value_type(self):
        return ScalarType(int)


class ReferenceExpression(Expression):
    __slots__ = []

    @property
    def canonical_form(self):
        return self.variable_name

    @property
    def variable_name(self):
        return self.ast.variable_name

    @property
    def variable(self):
        try:
            return self.context.variable_mapping[self.variable_name]
        except KeyError:
            return None

    @property
    def indices(self):
        return tuple(
            Expression.compile(index, self.context)
            for index in self.ast.indices
        )

    @property
    def value_type(self):
        value_type = self.variable.value_type
        for _ in self.indices:
            value_type = value_type.item_type
        return value_type

    def do_evaluate(self, context):
        ref = VariableReference(
            context=context,
            variable=self.variable,
        )
        for index in self.indices:
            ref = ArrayItemReference(
                array_type=ref.value_type,
                array=ref.get(),
                index=index.evaluate_in(context).get(),
            )
        return ref

    def validate(self, lvalue=False):
        if not self.variable:
            yield Diagnostic(Diagnostic.Messages.VARIABLE_NOT_DECLARED, self.variable_name, parseinfo=self.ast.parseinfo)
        elif self.variable not in self.context.initialized_variables and not lvalue:
            yield Diagnostic(Diagnostic.Messages.VARIABLE_NOT_INITIALIZED, self.variable.name, parseinfo=self.ast.parseinfo)
        elif isinstance(self.variable.value_type, ArrayType):
            if self.variable not in [t[0] for t in self.context.allocated_variables if t]:
                yield Diagnostic(Diagnostic.Messages.VARIABLE_NOT_ALLOCATED, self.variable.name, parseinfo=self.ast.parseinfo)
            for index in self.indices:
                yield from index.validate()
            if lvalue:
                for index in self.indices:
                    if isinstance(index, LiteralExpression):
                        yield Diagnostic(Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, index.value, parseinfo=self.ast.parseinfo)
                    elif index.variable not in self.context.index_variables:
                        yield Diagnostic(Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, index.variable_name, parseinfo=self.ast.parseinfo)


expression_classes = frozenbidict({
    "int_literal": IntLiteralExpression,
    "reference": ReferenceExpression,
})
