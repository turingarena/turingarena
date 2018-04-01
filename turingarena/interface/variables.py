from collections import namedtuple

from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import compile_type_expression
from turingarena.interface.exceptions import Diagnostic


class Variable(namedtuple("Variable", ["name", "value_type"])):
    @property
    def metadata(self):
        return dict(
            name=self.name,
            type=self.value_type.metadata,
        )


class VarStatement(Statement):
    __slots__ = []

    @property
    def type_expression(self):
        return compile_type_expression(self.ast.type, self.context)

    @property
    def value_type(self):
        return self.type_expression.value_type

    @property
    def variables(self):
        return tuple(
            Variable(value_type=self.value_type, name=d.name)
            for d in self.ast.declarators
        )

    @property
    def context_after(self):
        return self.context.with_variables(self.variables)

    def validate(self):
        for var in self.variables:
            if var.name in self.context.variable_mapping.keys():
                yield Diagnostic(f"variable {var.name} redeclared", parseinfo=self.ast.parseinfo)

