import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper, Instruction
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.statements.statement import SyntheticStatement
from turingarena_impl.interface.variables import Variable, TypeExpression, ScalarType

logger = logging.getLogger(__name__)

CallableSignature = namedtuple("CallableSignature", ["name", "parameters", "has_return_value"])


class ParameterDeclaration(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def type_expression(self):
        return TypeExpression(self.ast, self.context)

    @property
    def variable(self):
        return Variable(
            value_type=self.type_expression.value_type,
            name=self.ast.name
        )


class Callable(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def name(self):
        return self.ast.prototype.name

    @property
    def parameter_declarations(self):
        return tuple(
            ParameterDeclaration(ast=p, context=self.context)
            for p in self.ast.prototype.parameters
        )

    @property
    def parameters(self):
        return tuple(p.variable for p in self.parameter_declarations)

    @property
    def has_return_value(self):
        return self.ast.prototype.type == 'function'

    def validate(self):
        pass

    @property
    def signature(self):
        return CallableSignature(
            name=self.name,
            parameters=self.parameters,
            has_return_value=self.has_return_value,
        )

    @property
    def is_function(self):
        return self.has_return_value

    @property
    def is_procedure(self):
        return not self.has_return_value


class Function(Callable):
    __slots__ = []

    @property
    def callbacks_signature(self):
        if not self.ast.callbacks:
            return ()
        return tuple(
            CallableSignature(
                name=callback.prototype.name,
                has_return_value=callback.prototype.type == 'function',
                parameters=tuple(
                    ParameterDeclaration(ast=p, context=self.context)
                    for p in callback.prototype.parameters
                )
            )
            for callback in self.ast.callbacks
        )

    @property
    def has_callbacks(self):
        return bool(self.callbacks_signature)

    def validate(self):
        if self.has_callbacks:
            for callback_signature in self.callbacks_signature:
                for parameter in callback_signature.parameters:
                    if parameter.type_expression.value_type.meta_type != 'scalar':
                        yield Diagnostic(
                            Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS,
                            parseinfo=self.ast.parseinfo
                        )


class SyntheticCallbackBody(namedtuple("SyntheticCallbackBody", ["context", "body"])):
    @property
    def synthetic_statements(self):
        callback_index = self.context.callback_index
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
            context=self.context.local_context.create_inner().with_variables(self.parameters),
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

    def generate_instructions(self, bindings):
        inner_bindings = {
            **bindings,
            **{
                p.name: [None] for p in self.parameters
            }
        }
        yield CallbackCallInstruction(self, bindings=inner_bindings)
        yield from self.body.generate_instructions(inner_bindings)


class CallbackCallInstruction(Instruction, namedtuple("CallbackCallInstruction", [
    "callback", "bindings",
])):
    def on_generate_response(self):
        parameters = [
            self.bindings[p.name][0]
            for p in self.callback.parameters
        ]

        assert all(isinstance(v, int) for v in parameters)
        return (
            [1] +  # has callback
            [self.callback.context.callback_index] +
            parameters
        )
