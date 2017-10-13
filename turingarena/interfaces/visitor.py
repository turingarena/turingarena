import logging

logger = logging.getLogger(__name__)


def accept_statement(statement, *, visitor):
    return accept(
        statement,
        method_names=[
            "visit_" + statement.statement_type + "_statement",
            "visit_any_statement",
        ],
        visitor=visitor
    )


def accept_expression(expression, *, visitor):
    return accept(
        expression,
        method_names=[
            "visit_" + expression.expression_type + "_expression",
            "visit_any_expression",
        ],
        visitor=visitor
    )


def accept_type_expression(type_expression, *, visitor):
    return accept(
        type_expression,
        method_names=[
            "visit_" + type_expression.meta_type + "_type",
            "visit_any_type",
        ],
        visitor=visitor
    )


def accept(*args, method_names, visitor):
    try:
        ret = do_accept(args, method_names, visitor)
        return ret
    except:
        ret = "EXC"
        raise
    finally:
        logger.debug("visiting {visitor}({args}) -> {ret}".format(
            args=", ".join(repr(a) for a in args),
            visitor=type(visitor).__name__,
            ret=repr(ret),
        ))


def do_accept(args, method_names, visitor):
    for method_name in method_names:
        method = getattr(visitor, method_name, None)
        if method is not None:
            break
    else:
        raise NotImplementedError(*args)
    return method(*args)
