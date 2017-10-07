from turingarena.interfaces.analysis.block import compile_block
from turingarena.interfaces.analysis.declaration import process_simple_declaration, \
    process_declarators
from turingarena.interfaces.analysis.scope import Scope


import logging

from turingarena.interfaces.analysis.statement import accept_statement

logger = logging.getLogger(__name__)


class InterfaceCompiler:
    def __init__(self, interface):
        logger.debug("compiling interface {}".format(interface))

        self.interface = interface

        interface.variable_declarations = []
        interface.function_declarations = []
        interface.callback_declarations = []

        self.global_scope = Scope()

        for statement in interface.statements:
            statement.interface = interface
            logger.debug("compiling interface item {}".format(statement))
            accept_statement(statement, visitor=self)

    def visit_var_statement(self, statement):
        process_declarators(statement, scope=self.global_scope)
        self.interface.variable_declarations.append(statement)

    def visit_function_statement(self, statement):
        process_simple_declaration(statement, scope=self.global_scope)
        new_scope = Scope(self.global_scope)
        for p in statement.parameters:
            process_simple_declaration(p, scope=new_scope)
        self.interface.function_declarations.append(statement)

    def visit_callback_statement(self, statement):
        process_simple_declaration(statement, scope=self.global_scope)
        new_scope = Scope(self.global_scope)
        for p in statement.parameters:
            process_simple_declaration(p, scope=new_scope)
        compile_block(statement.body, scope=new_scope, outer_declaration=statement)
        self.interface.callback_declarations.append(statement)

    def visit_main_statement(self, statement):
        compile_block(statement.body, scope=self.global_scope, outer_declaration=statement)


compile_interface = InterfaceCompiler
