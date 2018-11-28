import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import MethodPrototype
from turingarena.driver.interface.context import InterfaceContext
from turingarena.driver.interface.parser import parse_interface

logger = logging.getLogger(__name__)


class InterfaceDefinition(namedtuple("InterfaceDefinition", [
    "constants",
    "methods",
    "main_block",
])):
    def diagnostics(self):
        # FIXME: should not reference the main_block to get a context
        return list(self.main_block.context.validate(self))

    @staticmethod
    def load(path):
        with open(path) as f:
            return InterfaceDefinition.compile(f.read())

    @staticmethod
    def compile(source_text, validate=False, descriptions=None):
        if descriptions is None:
            descriptions = {}

        ast = parse_interface(source_text)
        context = InterfaceContext(constants=(), methods=())
        for c in ast.constants_declarations:
            context = context.with_constant(
                context.constant_declaration(c)
            )

        for m in ast.method_declarations:
            context = context.with_method(
                context.prototype(MethodPrototype, m)
            )

        interface = InterfaceDefinition(
            constants=context.constants,
            methods=context.methods,
            main_block=context.main_block(ast.main_block),
        )
        if validate:
            for msg in interface.diagnostics():
                logger.warning(f"interface contains an error: {msg}")
        return interface
