import logging

from turingarena.common import TupleLikeObject
from turingarena.interface.block import InterfaceBody
from turingarena.interface.context import GlobalContext, MainContext
from turingarena.interface.driver.commands import MainBegin
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import Instruction
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.parser import parse_interface

logger = logging.getLogger(__name__)


class InterfaceSignature(TupleLikeObject):
    __slots__ = ["variables", "functions", "callbacks"]


class InterfaceDefinition(AbstractSyntaxNode):
    __slots__ = ["body", "source_text", "ast"]

    @staticmethod
    def compile(source_text, **kwargs):
        ast = parse_interface(source_text, **kwargs)

        body = InterfaceBody(ast.body)
        definition = InterfaceDefinition(source_text=source_text, ast=ast, body=body)
        definition.validate()
        return definition

    @property
    def global_variables(self):
        return self.body.declared_variables()

    @property
    def functions(self):
        return self.body.declared_functions()

    @property
    def callbacks(self):
        return {
            s.callback.name: s.callback
            for s in self.body.statements
            if s.statement_type == "callback"
        }

    def validate(self):
        self.body.validate()

    def contextualized_statements(self):
        return self.body.contextualized_statements()

    @property
    def signature(self):
        return InterfaceSignature(
            variables=self.body.declared_variables(),
            functions={
                c.name: c.signature
                for c in self.functions.values()
            },
            callbacks={
                c.name: c.signature
                for c in self.callbacks.values()
            },
        )

    def static_analysis(self):
        self.body.check_variables([], [])

    @property
    def main_body(self):
        [main] = [
            s.body
            for s, context in self.contextualized_statements()
            if s.statement_type == "main"
        ]
        return main

    @property
    def init_body(self):
        inits = [
            s.body
            for s, context in self.contextualized_statements()
            if s.statement_type == "init"
        ]
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
        variables = self.interface.signature.variables
        assert len(request.global_variables) == len(variables)
        for name, variable in variables.items():
            value = request.global_variables[name]
            self.global_context.bindings[variable] = variable.value_type.ensure(value)

    def on_generate_response(self):
        return []


class MainEndInstruction(Instruction):
    def on_generate_response(self):
        return []
