import logging

from turingarena.common import TupleLikeObject
from turingarena.interface.block import Block
from turingarena.interface.context import GlobalContext, MainContext, RootContext
from turingarena.interface.driver.commands import MainBegin
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import Instruction
from turingarena.interface.parser import parse_interface

logger = logging.getLogger(__name__)


class InterfaceSignature(TupleLikeObject):
    __slots__ = ["variables", "functions", "callbacks"]


class InterfaceDefinition(Block):
    __slots__ = ["source_text"]

    @staticmethod
    def compile(source_text, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        definition = InterfaceDefinition(
            source_text=source_text, ast=ast, context=RootContext(),
        )
        definition.validate()
        return definition

    @property
    def functions(self):
        return {
            s.function.name: s.function
            for s in self.statements
            if s.statement_type == "function"
        }

    @property
    def callbacks(self):
        return {
            s.callback.name: s.callback
            for s in self.statements
            if s.statement_type == "callback"
        }

    @property
    def global_variables(self):
        return self.declared_variables()

    @property
    def metadata(self):
        return dict(
            global_variables={
                v.name: v.metadata
                for v in self.global_variables.values()
            },
            callbacks={
                c.name: c.metadata
                for c in self.callbacks.values()
            },
            functions={
                f.name: f.metadata
                for f in self.functions.values()
            }
        )

    def static_analysis(self):
        self.check_variables([], [])

    @property
    def main_body(self):
        [main] = [s.body for s in self.statements if s.statement_type == "main"]
        return main

    @property
    def init_body(self):
        inits = [s.body for s in self.statements if s.statement_type == "init"]
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


class MainBeginInstruction(Instruction):
    __slots__ = ["interface", "global_context"]

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
