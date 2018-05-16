import logging

from turingarena import InterfaceExit
from turingarena_impl.interface.block import Block
from turingarena_impl.interface.callables import Function
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
            context=StaticGlobalContext(functions=self.functions).create_local()
        )

    def validate(self):
        for function in self.functions:
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

    # FIXME: the following properties could be taken from the context instead

    @property
    def functions(self):
        return tuple(
            Function(ast=func, context=StaticGlobalContext(functions=()))
            for func in self.ast.function_declarations
        )

    @property
    def function_map(self):
        return {f.name: f for f in self.functions}

    def generate_instructions(self):
        bindings = {}
        try:
            yield from self.main.generate_instructions(bindings)
        except InterfaceExit:
            pass
        yield ExitInstruction()
