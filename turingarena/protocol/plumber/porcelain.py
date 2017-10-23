import logging

from turingarena.protocol.visitor import accept_statement


logger = logging.getLogger(__name__)


class PorcelainRunner:

    def visit_any_statement(self, statement):
        logger.debug("visiting {}".format(statement))
        yield


def make_porcelain(interface):
    for statement in interface.variable_declarations:
        logger.debug("reading global variable {}".format(statement))

    for statement in interface.main.body.statements:
        yield from accept_statement(statement, visitor=PorcelainRunner())
