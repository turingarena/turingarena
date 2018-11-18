import logging

from turingarena.driver.client.exceptions import InterfaceError
from turingarena.driver.interface.block import Block
from turingarena.driver.interface.callables import MethodPrototype
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.context import InterfaceContext
from turingarena.driver.interface.execution import NodeExecutionContext
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.parser import parse_interface
from turingarena.driver.interface.statements.callback import Exit
from turingarena.driver.interface.statements.io import InitialCheckpoint
from turingarena.driver.interface.variables import Variable

logger = logging.getLogger(__name__)


class InterfaceExitNode(Exit):
    def _get_comment(self):
        return "terminate"


class InterfaceBody(Block):
    def _generate_flat_inner_nodes(self):
        yield InitialCheckpoint()
        yield from super()._generate_flat_inner_nodes()
        yield InterfaceExitNode()


class ConstantDeclaration(AbstractSyntaxNodeWrapper):
    @property
    def variable(self):
        return Variable(name=self.ast.name, dimensions=0)

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context.expression())


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
        return InterfaceBody(
            ast=self.ast.main_block,
            context=InterfaceContext(methods=self.methods, constants=self.constants).main_block_context
        )

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
        # FIXME: using a dummy context here
        return tuple(
            ConstantDeclaration(ast, InterfaceContext(methods=[], constants=[]).initial_context)
            for ast in self.ast.constants_declarations
        )

    def run_driver(self, context: NodeExecutionContext):
        description = "\n".join(self.main_block.node_description)
        logger.debug(f"Description: {description}")

        self.main_block.driver_run(context=context.with_assigments({
            c.variable.as_reference(): c.value.evaluate(context.bindings)
            for c in self.constants
        }))

        request = context.next_request()
        command = request.command
        if command != "exit":
            raise InterfaceError(f"expecting exit, got {command}")
