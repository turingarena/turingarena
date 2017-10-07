from turingarena.interfaces.analysis.statement import accept_statement

from turingarena.interfaces.analysis import block
from turingarena.interfaces.analysis.scope import Scope
from turingarena.interfaces.analysis.types import ScalarType


def process_declarators(declaration, *, scope):
    for declarator in declaration.declarators:
        scope[declarator.name] = declaration


def process_simple_declaration(declaration, *, scope):
    scope[declaration.declarator.name] = declaration
