import logging

from turingarena.protocol.visitor import accept_statement, accept_type_expression

logger = logging.getLogger(__name__)


class Deserializer:
    def __init__(self, plumber):
        self.plumber = plumber

    def visit_scalar_type(self, type_expression):
        t = {
            "int": int,
            "int64": int,
            "bool": bool,
            "str": str,
        }[type_expression.base]
        return t(self.plumber.receive())

    def visit_array_type(self, type_expression):
        size = int(self.plumber.receive())
        return [
            deserialize(
                type_expression=type_expression.item_type,
                plumber=self.plumber
            )
            for _ in range(size)
        ]


def deserialize(*, type_expression, plumber):
    logger.debug("deserializing type {}".format(type_expression))
    value = accept_type_expression(type_expression, visitor=Deserializer(plumber))
    logger.debug("value: {}".format(value))
    return value


class PorcelainRunner:
    def __init__(self, plumber):
        self.plumber = plumber

    def visit_call_statement(self, statement):
        command = self.plumber.receive()
        assert command == "call"
        function_name = self.plumber.receive()
        assert function_name == statement.function_name
        has_callbacks = bool(self.plumber.receive())

        logger.debug("receive call command (function_name={name}, has_callbacks={has_callbacks})".format(
            name=function_name,
            has_callbacks=has_callbacks,
        ))

        for arg in statement.function.declarator.parameters:
            deserialize(type_expression=arg.type, plumber=self.plumber)

    def visit_any_statement(self, statement):
        logger.debug("ignoring statement {}".format(statement))
        yield from []


def run_porcelain(plumber):
    logger.debug("reading global variables")
    command = plumber.receive()
    assert command == "globals"
    for statement in plumber.interface.variables:
        logger.debug("reading global variables {}".format(statement))
        for d in statement.declarators:
            logger.debug("reading global variable {}".format(d.name))
            deserialize(type_expression=statement.type, plumber=plumber)

    logger.debug("starting main procedure")
    run_body(plumber.interface.main.body, plumber=plumber)


def run_body(body, *, plumber):
    for statement in body.statements:
        yield from accept_statement(statement, visitor=PorcelainRunner(plumber))
