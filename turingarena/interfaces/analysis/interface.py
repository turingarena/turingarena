from turingarena.interfaces.analysis.block import compile_block
from turingarena.interfaces.analysis.declaration import compile_declaration
from turingarena.interfaces.analysis.scope import Scope


import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger, level=logging.DEBUG)


class InterfaceCompiler:
    def __init__(self, interface):
        logger.debug("compiling interface {}".format(interface))

        self.interface = interface

        interface.variable_declarations = []
        interface.function_declarations = []
        interface.callback_declarations = []

        self.global_scope = Scope()

        for item in interface.interface_items:
            item.interface = interface
            logger.debug("compiling interface item {}".format(item))
            item.accept(self)

    def visit_variable_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.variable_declarations.append(declaration)

    def visit_function_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.function_declarations.append(declaration)

    def visit_callback_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.callback_declarations.append(declaration)

    def visit_main_declaration(self, declaration):
        compile_block(declaration.body, scope=self.global_scope, outer_declaration=declaration)


compile_interface = InterfaceCompiler
