import logging
from collections import OrderedDict

from turingarena.protocol.analysis.block import compile_block
from turingarena.protocol.analysis.declaration import process_simple_declaration, \
    process_declarators
from turingarena.protocol.analysis.scope import Scope
from turingarena.protocol.visitor import accept_statement

logger = logging.getLogger(__name__)


class InterfaceCompiler:
    def __init__(self, interface):
        self.interface = interface

        interface.variables = []
        interface.functions = []
        interface.callbacks = []

        self.global_scope = Scope()

        for statement in interface.statements:
            statement.interface = interface
            logger.debug("compiling interface item {}".format(statement))
            accept_statement(statement, visitor=self)

    def visit_var_statement(self, statement):
        process_declarators(statement, scope=self.global_scope)
        self.interface.variables.append(statement)

    def visit_function_statement(self, statement):
        process_simple_declaration(statement, scope=self.global_scope)
        new_scope = Scope(self.global_scope)
        for p in statement.parameters:
            process_simple_declaration(p, scope=new_scope)
        self.interface.functions.append(statement)

    def visit_callback_statement(self, statement):
        process_simple_declaration(statement, scope=self.global_scope)
        new_scope = Scope(self.global_scope)
        for p in statement.parameters:
            process_simple_declaration(p, scope=new_scope)
        compile_block(statement.body, scope=new_scope, outer_declaration=statement)
        self.interface.callbacks.append(statement)

    def visit_main_statement(self, statement):
        compile_block(statement.body, scope=self.global_scope, outer_declaration=statement)
        self.interface.main = statement


compile_interface = InterfaceCompiler
