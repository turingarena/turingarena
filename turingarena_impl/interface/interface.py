import logging

from turingarena import InterfaceExit
from turingarena_impl.interface.block import Block
from turingarena_impl.interface.callables import MethodPrototype
from turingarena_impl.interface.context import StaticGlobalContext
from turingarena_impl.interface.parser import parse_interface
from turingarena_impl.interface.statements.exit import ExitInstruction
from turingarena_impl.loader import find_package_path

logger = logging.getLogger(__name__)


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        self.ast = ast
        self.main = Block(
            ast=self.ast.main_block,
            context=StaticGlobalContext(methods=self.methods).create_local()
        )

    def validate(self):
        for function in self.methods:
            yield from function.validate()
        yield from self.main.validate()

    @property
    def declared_variable(self):
        return self.main.context_after.variables

    @staticmethod
    def load(name):
        with open(find_package_path(name, "interface.txt")) as f:
            return InterfaceDefinition.compile(f.read())

    @staticmethod
    def compile(source_text, validate=True):
        interface = InterfaceDefinition(source_text)
        if validate:
            for msg in interface.validate():
                logger.warning(f"interface contains an error: {msg}")
        return interface

    @property
    def source_text(self):
        return self.ast.parseinfo.buffer.text

    @property
    def methods(self):
        return [
            MethodPrototype(ast=method, context=None)
            for method in self.ast.method_declarations
        ]

    def generate_instructions(self):
        bindings = {}
        try:
            yield from self.main.generate_instructions(bindings)
        except InterfaceExit:
            pass
        yield ExitInstruction()
