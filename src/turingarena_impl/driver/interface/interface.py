import logging

from turingarena.driver.exceptions import InterfaceError
from turingarena_impl.driver.interface.block import Block, BlockNode
from turingarena_impl.driver.interface.callables import MethodPrototype
from turingarena_impl.driver.interface.context import InterfaceContext
from turingarena_impl.driver.interface.execution import NodeExecutionContext
from turingarena_impl.driver.interface.parser import parse_interface
from turingarena_impl.driver.interface.variables import Reference, Variable

logger = logging.getLogger(__name__)


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text, descriptions):
        self.ast = parse_interface(source_text)
        self.descriptions = descriptions

    def diagnostics(self):
        return list(self.validate())

    def validate(self):
        for method in self.methods:
            yield from method.validate()
        yield from self.main_block.validate()

    @staticmethod
    def load(path):
        with open(path) as f:
            return InterfaceDefinition.compile(f.read())

    @staticmethod
    def compile(source_text, validate=True, descriptions={}):
        interface = InterfaceDefinition(source_text, descriptions)
        if validate:
            for msg in interface.validate():
                logger.warning(f"interface contains an error: {msg}")
        return interface

    @property
    def main_block(self):
        return Block(
            ast=self.ast.main_block,
            context=InterfaceContext(methods=self.methods, constants=self.constants).main_block_context()
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
            MethodPrototype(ast=method, context=None, description=self.descriptions.get(method.declarator.name))
            for method in self.ast.method_declarations
        ]

    @property
    def constants(self):
        return {
            c.name: c.value
            for c in self.ast.constants_declarations
        }

    @property
    def constants_references(self):
        return {
            Reference(variable=Variable(name=c.name, dimensions=0), index_count=0): int(c.value)
            for c in self.ast.constants_declarations
        }

    def run_driver(self, context: NodeExecutionContext):
        description = "\n".join(self.main_node.node_description)
        logger.debug(f"Description: {description}")

        ready_msg = context.receive_upward()
        assert ready_msg == (0,)
        context.report_ready()

        self.main_node.driver_run(context=context.with_assigments(self.constants_references))
        request = context.next_request()
        command = request.command
        if command != "exit":
            raise InterfaceError(f"expecting exit, got {command}")
