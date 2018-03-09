import logging
from collections import OrderedDict

from turingarena.common import TupleLikeObject
from turingarena.interface.body import Body
from turingarena.interface.driver.commands import MainBegin
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import ExecutableStructure, Instruction
from turingarena.interface.parser import parse_interface
from turingarena.interface.scope import Scope

logger = logging.getLogger(__name__)


class InterfaceSignature(TupleLikeObject):
    __slots__ = ["variables", "functions", "callbacks"]


class InterfaceDefinition(ExecutableStructure):
    __slots__ = ["signature", "body", "source_text", "ast"]

    @staticmethod
    def compile(source_text, **kwargs):
        ast = parse_interface(source_text, **kwargs)

        scope = Scope()
        body = Body.compile(ast.body, scope=scope)
        signature = InterfaceSignature(
            variables=OrderedDict(body.scope.variables.items()),
            functions={
                c.name: c.signature
                for c in body.scope.functions.values()
            },
            callbacks={
                c.name: c.signature
                for c in body.scope.callbacks.values()
            },
        )
        return InterfaceDefinition(
            source_text=source_text,
            ast=ast,
            signature=signature,
            body=body,
        )

    def unroll(self, frame):
        main = self.body.scope.main["main"]

        yield MainBeginInstruction(interface=self, global_frame=frame)
        try:
            yield from main.body.unroll(frame)
        except InterfaceExit:
            pass
        else:
            yield MainEndInstruction()


class MainBeginInstruction(Instruction):
    __slots__ = ["interface", "global_frame"]

    def run_driver_pre(self, request):
        assert isinstance(request, MainBegin)
        variables = self.interface.signature.variables
        assert len(request.global_variables) == len(variables)
        for name, variable in variables.items():
            value = request.global_variables[name]
            self.global_frame[variable] = variable.value_type.ensure(value)

    def run_driver_post(self):
        return []


class MainEndInstruction(Instruction):
    def run_driver_post(self):
        return []
