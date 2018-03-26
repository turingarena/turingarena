import logging

from turingarena.interface.block import Block
from turingarena.interface.context import GlobalContext, MainContext, RootContext
from turingarena.interface.driver.commands import MainBegin
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import Instruction
from turingarena.interface.parser import parse_interface

logger = logging.getLogger(__name__)


def parse_markdown(text):
    return text  # TODO


class InterfaceBody(Block):
    pass


class InterfaceDefinition:
    def __init__(self, source_text, extra_metadata, **kwargs):
        ast = parse_interface(source_text, **kwargs)
        self.extra_metadata = extra_metadata
        self.body = InterfaceBody(
            ast=ast, context=RootContext(),
        )
        self.body.validate()

    @staticmethod
    def compile(source_text, extra_metadata=None):
        if extra_metadata is None:
            extra_metadata = {}
        return InterfaceDefinition(source_text, extra_metadata=extra_metadata)

    @property
    def source_text(self):
        return self.body.ast.parseinfo.buffer.text

    @property
    def functions(self):
        return {
            s.function.name: s.function
            for s in self.body.statements
            if s.statement_type == "function"
        }

    @property
    def callbacks(self):
        return {
            s.callback.name: s.callback
            for s in self.body.statements
            if s.statement_type == "callback"
        }

    @property
    def global_variables(self):
        return self.body.declared_variables()

    def global_variable_metadata(self, v):
        extra = self.extra_metadata.get("global_variables", {}).get(v.name, {})
        return {
            **v.metadata,
            **dict(
                doc=parse_markdown(extra.get("doc", {})),
            )
        }

    def parameter_metadata(self, p, extra):
        return {
            **p.metadata,
            **dict(
                doc=parse_markdown(extra.get(p.name, {}).get("doc", "")),
            ),
        }

    def callable_metadata(self, c, extra):
        extra = extra.get(c.name, {})
        return {
            **c.metadata,
            **dict(
                parameters={
                    p.name: self.parameter_metadata(p, extra.get("parameters", {}))
                    for p in c.parameters
                },
            )
        }

    @property
    def metadata(self):
        return dict(
            global_variables={
                v.name: self.global_variable_metadata(v)
                for v in self.global_variables.values()
            },
            callbacks={
                c.name: self.callable_metadata(c, self.extra_metadata.get("callbacks", {}))
                for c in self.callbacks.values()
            },
            functions={
                f.name: self.callable_metadata(f, self.extra_metadata.get("functions", {}))
                for f in self.functions.values()
            }
        )

    def static_analysis(self):
        self.body.check_variables([], [])

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
