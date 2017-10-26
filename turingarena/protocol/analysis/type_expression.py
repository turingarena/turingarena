from turingarena.protocol.types import scalar, array


class TypeExpressionCompiler:
    def compile_scalar(self, expr):
        base_type = {"int": int, "bool": bool, }[expr.base]
        expr.descriptor = scalar(base_type)

    def compile_array(self, expr):
        compile_type_expression(expr.item_type)
        expr.descriptor = array(expr.item_type.descriptor)


def compile_type_expression(expr):
    compiler = TypeExpressionCompiler()
    getattr(compiler, "compile_" + expr.meta_type)(expr)
