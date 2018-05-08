import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper, Instruction
from turingarena_impl.interface.context import CallbackContext
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.references import VariableReference
from turingarena_impl.interface.statements.statement import SyntheticStatement
from turingarena_impl.interface.variables import Variable, TypeExpression, ScalarType

logger = logging.getLogger(__name__)

CallableSignature = namedtuple("CallableSignature", ["name", "parameters", "return_type"])


class ParameterDeclaration(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def type_expression(self):
        return TypeExpression(self.ast, self.context)

    @property
    def variable(self):
        return Variable(
            value_type=self.type_expression.value_type,
            name=self.ast.prototype.name if self.type_expression.value_type.meta_type == "callback" else self.ast.name
        )


class Callable(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def name(self):
        return self.ast.prototype.name

    @property
    def parameter_declarations(self):
        return tuple(
            ParameterDeclaration(p, self.context)
            for p in self.ast.prototype.parameters
        )

    @property
    def parameters(self):
        return tuple(p.variable for p in self.parameter_declarations)

    @property
    def return_type(self):
        return ScalarType(int) if self.ast.prototype.return_type == 'int' else None

    def validate(self):
        if self.return_type is not None and not isinstance(self.return_type, ScalarType):
            yield Diagnostic(
                Diagnostic.Messages.RETURN_TYPE_MUST_BE_SCALAR,
                parseinfo=self.ast.declarator.return_type.parseinfo,
            )

    @property
    def signature(self):
        return CallableSignature(
            name=self.name,
            parameters=self.parameters,
            return_type=self.return_type,
        )

    @property
    def metadata(self):
        return dict(
            return_value=None if self.return_type is None else dict(
                type=self.return_type.metadata,
            ),
        )


class Function(Callable):
    __slots__ = []


class SyntheticCallbackBody(namedtuple("SyntheticCallbackBody", ["context", "body"])):
    @property
    def synthetic_statements(self):
        callback_index = 42 # TODO: calculate callback index # len(self.context.callbacks)
        yield SyntheticStatement("write", arguments=[
            SyntheticExpression("int_literal", value=1),  # more callbacks
        ])
        yield SyntheticStatement("write", arguments=[
            SyntheticExpression("int_literal", value=callback_index),
        ])
        yield from self.body.synthetic_statements


class Callback(Callable):
    __slots__ = []

    @property
    def synthetic_body(self):
        return SyntheticCallbackBody(
            self.context,
            self.body,
        )

    @property
    def body(self):
        # TODO: generate block if body is None ('default' is specified)
        return Block(
            ast=self.ast.body,
            context=self.context.create_inner().with_variables(self.parameters),
        )

    def validate(self):
        yield from super().validate()

        invalid_parameter = next(
            (
                a for p, a in zip(self.parameters, self.ast.prototype.parameters)
                if not isinstance(p.value_type, ScalarType)
            ),
            None
        )

        if invalid_parameter is not None:
            yield Diagnostic(
                Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS,
                parseinfo=invalid_parameter.parseinfo,
            )

    def generate_instructions(self, context):
        global_context = context.call_context.local_context.procedure.global_context
        callback_context = CallbackContext(
            accept_context=context,
            global_context=global_context,
        )

        local_context = callback_context.child({p.name: p for p in self.parameters})
        yield CallbackCallInstruction(
            callback_context=callback_context,
            local_context=local_context,
        )
        yield from self.body.generate_instructions(local_context)


class CallbackCallInstruction(Instruction, namedtuple("CallbackCallInstruction", ["callback_context", "local_context"])):
    @property
    def callback(self):
        return self.callback_context.accept_context.callback

    def on_generate_response(self):
        parameters = [
            VariableReference(
                context=self.local_context,
                variable=p,
            ).get()
            for p in self.callback.parameters
        ]

        assert all(isinstance(v, int) for v in parameters)
        accepted_callbacks = list(self.callback_context.accept_context.call_context.accepted_callbacks.keys())
        return (
            [1] +  # has callback
            [accepted_callbacks.index(self.callback.name)] +
            parameters
        )


