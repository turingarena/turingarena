import logging
from collections import namedtuple

from turingarena import InterfaceExit
from turingarena.driver.commands import MainBegin
from turingarena_impl.interface.block import Block
from turingarena_impl.interface.context import GlobalContext, MainContext, StaticGlobalContext
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.parser import parse_interface
from turingarena_impl.loader import find_package_path
from turingarena_impl.interface.callables import Function

logger = logging.getLogger(__name__)


class InterfaceDefinition:
    def __init__(self, source_text, extra_metadata, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        logger.debug(f"Parsed interface {ast}")
        self.extra_metadata = extra_metadata
        self.ast = ast
        self.main = Block(
            ast=self.ast.main_block,
            context=StaticGlobalContext(functions=self.functions).create_local()
        )

    def validate(self):
        yield from self.main.validate()

    @property
    def declared_variable(self):
        return self.main.context_after.variables

    @staticmethod
    def load(name):
        with open(find_package_path(name, "interface.txt")) as f:
            return InterfaceDefinition.compile(f.read())

    @staticmethod
    def compile(source_text, extra_metadata=None, validate=True):
        if extra_metadata is None:
            extra_metadata = {}
        interface = InterfaceDefinition(source_text, extra_metadata=extra_metadata)
        if validate:
            for msg in interface.validate():
                logger.warning(f"interface contains an error: {msg}")
        return interface

    @property
    def source_text(self):
        return self.ast.parseinfo.buffer.text

    @property
    def functions(self):
        return tuple(
            Function(ast=func, context=StaticGlobalContext(functions=()))
            for func in self.ast.function_declarations
        )

    @property
    def function_map(self):
        return {f.name: f for f in self.functions}

    # FIXME: the following properties could be taken from the context instead

    def parameter_metadata(self, p, extra):
        return {
            **extra.get(p.name, {}),
            **p.metadata,
        }

    def callable_metadata(self, c, extra):
        extra = extra.get(c.name, {})
        return {
            **extra,
            **c.metadata,
            **dict(
                return_value={
                    **extra.get("return_value", {}),
                    **c.metadata["return_value"],
                },
                parameters={
                    p.name: self.parameter_metadata(p, extra.get("parameters", {}))
                    for p in c.parameters
                },
            )
        }

    @property
    def metadata(self):
        return {
            **self.extra_metadata,
            **dict(
                callbacks={
                    c.name: self.callable_metadata(c, self.extra_metadata.get("callbacks", {}))
                    for c in self.callbacks
                },
                functions={
                    f.name: self.callable_metadata(f, self.extra_metadata.get("functions", {}))
                    for f in self.functions
                }
            ),
        }

    def generate_instructions(self):
        global_context = GlobalContext(self)
        main_context = MainContext(global_context=global_context)

        yield MainBeginInstruction(interface=self, global_context=global_context)
        try:
            yield from self.main.generate_instructions(main_context)
        except InterfaceExit:
            pass
        else:
            yield MainEndInstruction()


class MainBeginInstruction(Instruction, namedtuple("MainBeginInstruction", [
    "interface", "global_context"
])):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, MainBegin)

    def on_generate_response(self):
        return []


class MainEndInstruction(Instruction):
    def on_generate_response(self):
        return []
