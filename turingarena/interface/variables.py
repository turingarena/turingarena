from collections import namedtuple

from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import ValueType

Variable = namedtuple("Variable", ["name", "value_type"])


class VarStatement(Statement):
    __slots__ = []

    @property
    def value_type(self):
        return ValueType.compile(self.ast.type.expression)

    @property
    def variables(self):
        # FIXME: for skeleton generation
        return self.declared_variables()

    def declared_variables(self):
        return [
            Variable(value_type=self.value_type, name=d.name)
            for d in self.ast.declarators
        ]
