from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.expressions import IntLiteral, VariableReference
from turingarena.util.visitor import visitormethod


class Validator:
    @visitormethod
    def validate(self, n):
        return []

    def validate_InterfaceDefinition(self, n):
        for method in n.methods:
            yield from self.validate(method)
        yield from self.validate(n.main_block)

    def validate_Read(self, n):
        for exp in n.arguments:
            yield from self.validate_reference_declaration(exp)

    def validate_Write(self, n):
        for exp in n.arguments:
            yield from self.validate(exp)

    def validate_Switch(self, n):
        yield from self.validate(n.value)

        if len(n.cases) == 0:
            yield Diagnostic(Diagnostic.Messages.EMPTY_SWITCH_BODY, parseinfo=n.ast.parseinfo)

        labels = []
        for case in n.cases:
            for label in case.labels:
                if label in labels:
                    yield Diagnostic(Diagnostic.Messages.DUPLICATED_CASE_LABEL, label, parseinfo=n.ast.parseinfo)
                labels.append(label)
            yield from self.validate(case)

    def validate_Case(self, n):
        for l in n.labels:
            if not isinstance(l, IntLiteral):
                yield Diagnostic(
                    Diagnostic.Messages.SWITCH_LABEL_NOT_LITERAL,
                    parseinfo=n.ast.labels.parseinfo,
                )
        yield from self.validate(n.body)

    def validate_CallbackImplementation(self, n):
        yield from self.validate(n.prototype)

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

    def validate_CallArgumentsResolve(self, n):
        method = n.method
        if method is None:
            return

        if len(n.arguments) != len(method.parameters):
            yield Diagnostic(
                Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER,
                method.name, len(method.parameters), len(n.arguments),
                parseinfo=n.ast.parseinfo,
            )
        for parameter_declaration, expression in zip(method.parameter_declarations, n.arguments):
            yield from self.validate(expression)
            dimensions = self.dimensions(expression)
            if dimensions != parameter_declaration.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter_declaration.variable.name,
                    method.name,
                    parameter_declaration.dimensions,
                    dimensions,
                    parseinfo=expression.ast.parseinfo,
                )

    def validate_CallReturn(self, n):
        method = n.method
        if method is None:
            return

        if n.return_value is not None:
            yield from self.validate_reference_declaration(n.return_value)

    def validate_IntermediateNode(self, n):
        return ()

    def validate_VariableReference(self, e):
        if not e.variable_name in self.reference_declaration_mapping:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_NOT_DECLARED,
                e.variable_name,
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

    def _validate_reference_declaration_VariableReference(self, e, index_count):
        if e.variable_name in self.reference_declaration_mapping:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_REUSED,
                e.variable_name,
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

        if not isinstance(e.index, VariableReference) or e.index.variable_name != expected_index.variable.name:
            yield Diagnostic(
                Diagnostic.Messages.WRONG_ARRAY_INDEX,
                expected_index.variable.name,
                parseinfo=e.index.ast.parseinfo,
            )

    def _validate_reference_declaration_IntLiteral(self, e, index_count):
        yield "unexpected literal"  # TODO: make a Diagnostic
