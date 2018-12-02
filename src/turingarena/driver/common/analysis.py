from turingarena.driver.common.nodes import *
from turingarena.driver.compile.analysis import ReferenceDefinition, ReferenceResolution
from turingarena.driver.gen.nodes import VariableDeclaration, Alloc
from turingarena.util.visitor import visitormethod


class InterfaceAnalyzer:
    def reference_actions(self, n):
        return list(self._get_reference_actions(n))

    @visitormethod
    def _get_reference_actions(self, n):
        pass

    def _get_reference_actions_Read(self, n):
        for exp in n.arguments:
            yield self.create_reference_definition(exp)

    def _get_reference_actions_Write(self, n):
        for exp in n.arguments:
            yield ReferenceResolution(exp)

    def _get_reference_actions_SwitchValueResolve(self, n):
        yield ReferenceResolution(n.value)

    def _get_reference_actions_CallbackStart(self, n):
        for p in n.prototype.parameters:
            yield ReferenceDefinition(p, dimensions=0)

    def _get_reference_actions_Return(self, n):
        yield ReferenceResolution(n.value)

    def _get_reference_actions_For(self, n):
        for a in self.reference_actions(n.body):
            r = a.reference
            if isinstance(r, Subscript):
                reference = r.array
                if isinstance(a, ReferenceDefinition):
                    yield a._replace(reference=reference, dimensions=a.dimensions + 1)
                if isinstance(a, ReferenceResolution):
                    yield a._replace(reference=reference)

    def _get_reference_actions_Call(self, n):
        for p in n.arguments:
            yield ReferenceResolution(p)
        if n.return_value is not None:
            yield self.create_reference_definition(n.return_value)

    def _get_reference_actions_Block(self, n):
        for child in n.children:
            yield from self.reference_actions(child)

    def _get_reference_actions_Step(self, n):
        yield from self.reference_actions(n.body)

    def _get_reference_actions_object(self, n):
        return []

    def create_reference_definition(self, e, dimensions=0):
        return self._create_reference_definition(e, dimensions)

    @visitormethod
    def _create_reference_definition(self, e, dimensions):
        pass

    def _create_reference_definition_Variable(self, e, dimensions):
        return ReferenceDefinition(
            reference=e,
            dimensions=dimensions,
        )

    def _create_reference_definition_Subscript(self, e, dimensions):
        array_declaration = self.create_reference_definition(e.array, dimensions + 1)
        if array_declaration is not None:
            return ReferenceDefinition(
                reference=e,
                dimensions=array_declaration.dimensions - 1,
            )

    def _create_reference_definition_object(self, e):
        return None

    @visitormethod
    def is_reference(self, e):
        pass

    def is_reference_Variable(self, e):
        return True

    def is_reference_Subscript(self, e):
        # FIXME: we should check that the index is the one expected (should we?)
        return self.is_reference(e.array) and isinstance(e.index, Variable)

    def variable_declarations(self, n):
        return frozenset(self._get_variable_declarations(n))

    def _get_variable_declarations(self, n):
        types = [Read, Call, For]

        if not any(isinstance(n, t) for t in types):
            return
        for a in self.reference_actions(n):
            if isinstance(a, ReferenceDefinition) and isinstance(a.reference, Variable):
                yield VariableDeclaration(a.reference, a.dimensions)

    def reference_allocations(self, n):
        return list(self._get_allocations(n))

    @visitormethod
    def _get_allocations(self, n):
        pass

    def _get_allocations_For(self, n):
        for a in self.reference_actions(n):
            if not isinstance(a, ReferenceDefinition):
                continue
            assert a.dimensions > 0
            yield Alloc(
                reference=a.reference,
                dimensions=a.dimensions - 1,
                size=n.index.range,
            )

    def _get_allocations_object(self, n):
        return []
