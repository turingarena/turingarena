import logging
from collections import namedtuple

from turingarena import InterfaceExit
from turingarena.driver.commands import MainBegin
from turingarena_impl.interface.block import Block
from turingarena_impl.interface.context import GlobalContext, MainContext, RootContext
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.executable import Instruction
from turingarena_impl.interface.parser import parse_interface
from turingarena_impl.loader import find_package_path

logger = logging.getLogger(__name__)


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        self.body = InterfaceBody(
            ast=ast, context=RootContext(),
        )

    def validate(self):
        if self.global_variables and not self.init_body:
            yield Diagnostic(Diagnostic.Messages.INIT_BLOCK_MISSING, parseinfo=self.body.ast.parseinfo)
        yield from self.body.validate()

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
