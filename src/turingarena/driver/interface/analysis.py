import logging

from turingarena.driver.interface.nodes import CallbackStart, For, CallReturn, AcceptCallbacks, Read, Checkpoint, Loop, \
    Variable, Subscript, Call
from turingarena.driver.interface.requests import RequestSignature, CallRequestSignature
from turingarena.driver.interface.variables import ReferenceResolution, ReferenceDefinition, \
    ReferenceDirection, VariableDeclaration, ReferenceAllocation
from turingarena.util.visitor import visitormethod


class TreeAnalyzer:
    DIRECTION_MAP = {
        ReferenceDirection.DOWNWARD: [
            Read,
        ],
        ReferenceDirection.UPWARD: [
            Checkpoint,
            CallbackStart,
            CallReturn,
        ],
    }

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

    def can_be_grouped(self, n):
        ans = self._can_be_grouped(n)
        logging.debug(f"can_be_grouped({n}) -> {ans}")
        return ans

    @visitormethod
    def _can_be_grouped(self, n):
        pass

    def _can_be_grouped_For(self, n):
        # no local references
        return all(
            isinstance(a.reference, Subscript)
            for a in self.reference_actions(n.body)
        ) and self.can_be_grouped(n.body)

    def _can_be_grouped_Block(self, n):
        return all(
            self.can_be_grouped(child)
            for child in n.children
        )

    def _can_be_grouped_Step(self, n):
        return self.can_be_grouped(n.body)

    def _can_be_grouped_object(self, n):
        for t in [
            Loop,
            AcceptCallbacks,
        ]:
            if isinstance(n, t):
                return False
        return True

    def declaration_directions(self, n):
        return frozenset(self._get_directions(n))

    @visitormethod
    def _get_directions(self, n):
        pass

    def _get_directions_Block(self, n):
        for child in n.children:
            yield from self.declaration_directions(child)

    def _get_directions_Step(self, n):
        if n.direction is not None:
            yield n.direction

    def _get_directions_For(self, n):
        yield from self.declaration_directions(n.body)

    def _get_directions_If(self, n):
        yield from self.declaration_directions(n.then_body)
        if n.else_body is not None:
            yield from self.declaration_directions(n.else_body)

    def _get_directions_Switch(self, n):
        for c in n.cases:
            yield from self.declaration_directions(c.body)

    def _get_directions_Loop(self, n):
        yield from self.declaration_directions(n.body)

    def _get_directions_AcceptCallbacks(self, n):
        for callback in n.callbacks:
            yield from self.declaration_directions(callback.body)

    def _get_directions_CallbackImplementation(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_object(self, n):
        for d, ts in self.DIRECTION_MAP.items():
            for t in ts:
                if isinstance(n, t):
                    yield d

    def first_requests(self, n):
        return frozenset(self._get_first_requests(n))

    @visitormethod
    def _get_first_requests(self, n):
        pass

    def _get_first_requests_Exit(self, n):
        yield RequestSignature("exit")

    def _get_first_requests_Call(self, n):
        yield CallRequestSignature("call", n.method.name)

    def _get_first_requests_Block(self, n):
        for child in n.children:
            for r in self.first_requests(child):
                if r is not None:
                    yield r
            if None not in self.first_requests(child):
                break
        else:
            yield None

    def _get_first_requests_Step(self, n):
        return self.first_requests(n.body)

    def _get_first_requests_For(self, n):
        yield None
        yield from self.first_requests(n.body)

    def _get_first_requests_Loop(self, n):
        yield None
        yield from self.first_requests(n.body)

    def _get_first_requests_Switch(self, n):
        for c in n.cases:
            yield from self.first_requests(c.body)

    def _get_first_requests_If(self, n):
        yield from self.first_requests(n.then_body)
        if n.else_body is not None:
            yield from self.first_requests(n.else_body)
        else:
            yield None

    def _get_first_requests_object(self, n):
        yield None

    @visitormethod
    def is_reference(self, e):
        pass

    def is_reference_Variable(self, e):
        return True

    def is_reference_Subscript(self, e):
        # FIXME: we should check that the index is the one expected (should we?)
        return self.is_reference(e.array) and isinstance(e.index, Variable)

    def create_reference_definition(self, e, dimensions=0):
        return self._create_reference_definition(e, dimensions)

    @visitormethod
    def _create_reference_definition(self, e, dimensions):
        pass

    def _create_reference_definition_Variable(self, e, dimensions):
        return ReferenceDefinition(
            reference=Variable(name=e.name),
            dimensions=dimensions,
        )

    def _create_reference_definition_Subscript(self, e, dimensions):
        array_declaration = self.create_reference_definition(e.array, dimensions + 1)
        if array_declaration is not None:
            return ReferenceDefinition(
                reference=Subscript(
                    array=array_declaration.reference,
                    index=e.index,
                ),
                dimensions=array_declaration.dimensions - 1,
            )

    def _create_reference_definition_object(self, e):
        return None

    def comment(self, n):
        return self._get_comment(n)

    @visitormethod
    def _get_comment(self, n):
        pass

    def _get_comment_MainExit(self, n):
        return "terminate"

    def _get_comment_PrintCallbackRequest(self, n):
        return "callback '{n.prototype.name}' (index: {n.index})"

    def _get_comment_PrintNoCallbacks(self, n):
        return "no more callbacks"

    def _get_comment_object(self, n):
        return None

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
            yield ReferenceAllocation(
                reference=a.reference,
                dimensions=a.dimensions - 1,
                size=n.index.range,
            )

    def _get_allocations_object(self, n):
        return []
