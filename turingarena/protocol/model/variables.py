from turingarena.common import ImmutableObject
from turingarena.protocol.model.statement import Statement
from turingarena.protocol.model.type_expressions import ValueType


class Variable(ImmutableObject):
    __slots__ = ["value_type", "name"]


class VarStatement(Statement):
    __slots__ = ["value_type", "variables"]

    @staticmethod
    def compile(ast, scope):
        value_type = ValueType.compile(ast.type.expression, scope=scope)
        variables = [
            Variable(value_type=value_type, name=d.name)
            for d in ast.declarators
        ]
        for v in variables:
            scope.variables[v.name] = v
        return VarStatement(
            value_type=value_type,
            variables=variables
        )
