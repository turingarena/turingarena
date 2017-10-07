def accept_statement(statement, *, visitor):
    return accept(
        statement,
        method_name="visit_" + statement.statement_type + "_statement",
        default_method_name="visit_any_statement",
        visitor=visitor
    )


def accept_expression(expression, *, visitor):
    return accept(
        expression,
        method_name="visit_" + expression.expression_type + "_expression",
        default_method_name="visit_any_expression",
        visitor=visitor
    )


def accept(item, *, method_name, default_method_name=None, visitor):
    try:
        method = getattr(visitor, method_name)
    except AttributeError:
        try:
            method = getattr(visitor, default_method_name)
        except AttributeError:
            method = None
    if method is None:
        raise NotImplementedError(item)
    return method(item)
