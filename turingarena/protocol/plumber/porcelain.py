from turingarena.protocol.visitor import accept_statement


class PorcelainRunner:

    def visit_any_statement(self, statement):
        print(statement)
        yield


def make_porcelain(interface):
    for statement in interface.main:
        accept_statement(statement, visitor=PorcelainRunner())
