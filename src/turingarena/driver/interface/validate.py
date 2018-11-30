from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.nodes import Variable
from turingarena.util.visitor import visitormethod


class Validator:
    @visitormethod
    def validate(self, n):
        return []

    def validate_Return(self, n):
        yield from self.validate_reference_declaration(n.value)

    def validate_SequenceNode(self, n):
        for child in n.children:
            yield from self.validate(child)

    def validate_MethodPrototype(self, n):
        for callback in n.callbacks:
            yield from self.validate(callback)

    def validate_CallbackPrototype(self, n):
        for callback in n.callbacks:
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_CALLBACK,
                callback.name,
                parseinfo=callback.ast.parseinfo,
            )
        for parameter in n.parameter_declarations:
            if parameter.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS,
                    parseinfo=parameter.ast.parseinfo,
                )

    def validate_For(self, n):
        yield from self.validate(n.index.range)
        yield from self.validate(n.body)

    def validate_Loop(self, n):
        yield from self.validate(n.body)

    def validate_Break(self, n):
        if not self.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=n.ast.parseinfo)

    def validate_If(self, n):
        yield from self.validate(n.condition)
        for branch in n.branches:
            yield from self.validate(branch)

    def validate_Call(self, n):
        if n.method_name not in n.context.global_context.methods_by_name:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_NOT_DECLARED,
                n.method_name,
                parseinfo=n.ast.parseinfo,
            )
            return

        method = n.method
        if method.has_return_value and n.return_value is None:
            yield Diagnostic(
                Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, method.name,
                parseinfo=n.ast.parseinfo,
            )
        if not method.has_return_value and n.return_value is not None:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_DOES_NOT_RETURN_VALUE, method.name,
                parseinfo=n.ast.return_value.parseinfo,
            )

    def validate_Variable(self, e):
        if not e.name in self.reference_definitions:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_NOT_DECLARED,
                e.name,
                parseinfo=e.ast.parseinfo,
            )

    def validate_Subscript(self, e):
        yield from self.validate(e.array)
        yield from self.validate(e.index)

    def validate_IntLiteral(self, e):
        return ()

    @visitormethod
    def _validate_reference_declaration(self, e, index_count):
        pass

    def validate_reference_declaration(self, e, index_count=0):
        return self._validate_reference_declaration(e, index_count)

    def _validate_reference_declaration_Variable(self, e, index_count):
        if e.name in self.reference_definitions:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_REUSED,
                e.name,
                parseinfo=e.ast.parseinfo,
            )

    def _validate_reference_declaration_Subscript(self, e, index_count):
        yield from self.validate_reference_declaration(e.array, index_count + 1)
        yield from self.validate(e.index)

        reversed_indexes = self.index_variables[::-1]
        try:
            expected_index = reversed_indexes[index_count]
        except IndexError:
            expected_index = None

        if expected_index is None:
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_ARRAY_INDEX,
                parseinfo=e.index.ast.parseinfo,
            )
            return

        if not isinstance(e.index, Variable) or e.index.name != expected_index.variable.name:
            yield Diagnostic(
                Diagnostic.Messages.WRONG_ARRAY_INDEX,
                expected_index.variable.name,
                parseinfo=e.index.ast.parseinfo,
            )

    def _validate_reference_declaration_IntLiteral(self, e, index_count):
        yield "unexpected literal"  # TODO: make a Diagnostic
