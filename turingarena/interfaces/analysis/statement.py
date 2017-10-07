def accept_statement(statement, *, visitor):
    try:
        method = getattr(visitor, "visit_" + statement.statement_type + "_statement")
    except AttributeError:
        try:
            method = getattr(visitor, "visit_any_statement")
        except AttributeError:
            raise NotImplementedError(statement.statement_type)
    return method(statement)
