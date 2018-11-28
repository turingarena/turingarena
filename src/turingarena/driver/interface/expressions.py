import logging

from turingarena.driver.interface.nodes import IntLiteral, VariableReference, Subscript

logger = logging.getLogger(__name__)


class ExpressionCompiler:
    __slots__ = []

    def expression(self, ast):
        return getattr(self, f"_compile_{ast.expression_type}")(ast)

    def _compile_int_literal(self, ast):
        return IntLiteral(value=int(ast.int_literal))

    def _compile_reference_subscript(self, ast):
        return self._compile_subscript(ast, ast.indices)

    def _compile_subscript(self, ast, index_asts):
        if index_asts:
            array = self._compile_subscript(ast, index_asts[:-1])
            index = self.expression(index_asts[-1])
            return Subscript(array, index)
        else:
            return VariableReference(ast.variable_name)
