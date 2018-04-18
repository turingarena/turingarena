import logging
from collections import namedtuple

from turingarena.interface.block import Block
from turingarena.interface.context import GlobalContext, MainContext, RootContext
from turingarena.interface.driver.commands import MainBegin
from turingarena.interface.exceptions import InterfaceExit, Diagnostic
from turingarena.interface.executable import Instruction
from turingarena.interface.parser import parse_interface
from turingarena.loader import find_package_path, split_module

logger = logging.getLogger(__name__)


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text, extra_metadata, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        self.extra_metadata = extra_metadata
        self.body = InterfaceBody(
            ast=ast, context=RootContext(),
        )

    def validate(self):
        if self.global_variables and not self.init_body:
            yield Diagnostic(Diagnostic.Messages.INIT_BLOCK_MISSING, parseinfo=self.body.ast.parseinfo)
        yield from self.body.validate()

    @staticmethod
    def load(name):
        mod, rel_path = split_module(name, default_arg="interface.txt")
        with open(find_package_path(mod, rel_path)) as f:
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
        return self.body.ast.parseinfo.buffer.text

    # FIXME: the following properties could be taken from the context instead

    @property
    def functions(self):
        return tuple(
            s.function
            for s in self.body.statements
            if s.statement_type == "function"
        )

    @property
    def function_map(self):
        return {f.name: f for f in self.functions}

    @property
    def callbacks(self):
        return tuple(
            s.callback
            for s in self.body.statements
            if s.statement_type == "callback"
        )

    @property
    def callback_map(self):
        return {c.name: c for c in self.callbacks}

    @property
    def global_variables(self):
        return self.body.declared_variables

    def global_variable_metadata(self, v):
        return {
            **self.extra_metadata.get("global_variables", {}).get(v.name, {}),
            **v.metadata,
        }

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
                global_variables={
                    v.name: self.global_variable_metadata(v)
                    for v in self.global_variables.values()
                },
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

    @property
    def main_body(self):
        [main] = [s.body for s in self.body.statements if s.statement_type == "main"]
        return main

    @property
    def init_body(self):
        inits = [s.body for s in self.body.statements if s.statement_type == "init"]
        if inits:
            [init] = inits
            return init
        else:
            return None

    def generate_instructions(self):
        global_context = GlobalContext(self)
        main_context = MainContext(global_context=global_context)

        yield MainBeginInstruction(interface=self, global_context=global_context)
        try:
            if self.init_body is not None:
                yield from self.init_body.generate_instructions(main_context)
            yield from self.main_body.generate_instructions(main_context)
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
        variables = self.interface.global_variables
        assert len(request.global_variables) == len(variables)
        for name, variable in variables.items():
            value = request.global_variables[name]
            self.global_context.bindings[variable] = variable.value_type.ensure(value)

    def on_generate_response(self):
        return []


class MainEndInstruction(Instruction):
    def on_generate_response(self):
        return []
