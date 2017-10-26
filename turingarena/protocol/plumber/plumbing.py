import logging

from turingarena.protocol.visitor import accept_statement

logger = logging.getLogger(__name__)


class PlumbingRunner:
    def __init__(self, plumber):
        self.plumber = plumber

    def visit_input_statement(self, statement):
        yield from []

    def visit_any_statement(self, statement):
        logger.debug("ignoring statement {}".format(statement))
        yield from []


def make_plumbing(plumber):
    pass


def run_body(body, *, plumber):
    for statement in body.statements:
        yield from accept_statement(statement, visitor=PlumbingRunner(plumber))
