from turingarena.common import ImmutableObject
from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import ValueType


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
            ast=ast,
            value_type=value_type,
            variables=variables
        )
