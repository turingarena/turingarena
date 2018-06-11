import logging

from turingarena import InterfaceError
from turingarena_impl.interface.block import Block, BlockNode
from turingarena_impl.interface.callables import MethodPrototype
from turingarena_impl.interface.context import InterfaceContext
from turingarena_impl.interface.execution import NodeExecutionContext
from turingarena_impl.interface.parser import parse_interface
from turingarena_impl.loader import find_package_path

logger = logging.getLogger(__name__)


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text):
        ast = parse_interface(source_text)
        self.ast = ast

    def diagnostics(self):
        return list(self.validate())

    def validate(self):
        for method in self.methods:
            yield from method.validate()
        yield from self.main_block.validate()

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
    def main_block(self):
        return Block(
            ast=self.ast.main_block,
            context=InterfaceContext(methods=self.methods).main_block_context()
        )

    @property
    def main_node(self):
        return BlockNode.from_nodes(self.main_block.flat_inner_nodes)

    @property
    def source_text(self):
        return self.ast.parseinfo.buffer.text

    @property
    def methods(self):
        return [
            MethodPrototype(ast=method, context=None)
            for method in self.ast.method_declarations
        ]

    def run_driver(self, context: NodeExecutionContext):
        self.main_node.driver_run(context=context)
        command = context.receive_driver_downward()
        if command != "exit":
            raise InterfaceError(f"expecting exit, got {command}")
