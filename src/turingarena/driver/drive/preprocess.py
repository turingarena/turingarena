from turingarena.driver.common.nodes import *
from turingarena.driver.common.transform import TreeTransformer
from turingarena.driver.drive.analysis import ExecutionAnalyzer
from turingarena.driver.drive.nodes import *
from turingarena.util.visitor import visitormethod


class ExecutionPreprocessor(
    TreeTransformer,
    ExecutionAnalyzer,
):
    def can_be_grouped(self, n):
        return self._can_be_grouped(n)

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
        for body in n.branches:
            if body is not None:
                yield from self.declaration_directions(body)

    def _get_directions_Switch(self, n):
        for c in n.cases:
            yield from self.declaration_directions(c.body)

    def _get_directions_Loop(self, n):
        yield from self.declaration_directions(n.body)

    def _get_directions_AcceptCallbacks(self, n):
        for callback in n.callbacks:
            yield from self.declaration_directions(callback.body)

    def _get_directions_Callback(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_object(self, n):
        for d, ts in self.DIRECTION_MAP.items():
            for t in ts:
                if isinstance(n, t):
                    yield d

    def transform_Block(self, n):
        return n._replace(
            children=tuple(
                self.group_children(
                    self.expand_sequence(n.children)
                )
            ),
        )

    def transform_Callback(self, n):
        prepend_nodes = (CallbackStart(n.prototype),)
        if n.prototype.has_return_value:
            append_nodes = ()
        else:
            append_nodes = (CallbackEnd(),)
        return super().transform_Callback(n._replace(
            body=n.body._replace(
                children=prepend_nodes + n.body.children + append_nodes
            )
        ))

    def expand_sequence(self, ns):
        for n in ns:
            yield from self.node_replacement(n)

    @visitormethod
    def node_replacement(self, n):
        pass

    def node_replacement_object(self, n):
        yield self.transform(n)

    def node_replacement_If(self, n):
        yield IfConditionResolve(n)
        yield self.transform(n)

    def node_replacement_Switch(self, n):
        yield SwitchValueResolve(n)
        yield self.transform(n)

    def node_replacement_Call(self, n):
        yield CallArgumentsResolve(method=n.method, arguments=n.arguments)
        if n.method.callbacks:
            yield AcceptCallbacks(self.transform_all(n.callbacks))
        yield CallCompleted()
        if n.method.has_return_value:
            yield CallReturn(n.return_value)

    def group_children(self, children):
        group = []
        for node in children:
            can_be_grouped = self.can_be_grouped(node) and len(self._group_directions([node])) <= 1

            if can_be_grouped and len(self._group_directions(group + [node])) <= 1:
                group.append(node)
                continue

            if group:
                yield self._make_step(group)
                group.clear()

            if not can_be_grouped:
                yield node
            else:
                group.append(node)

        if group:
            yield self._make_step(group)

    def _make_step(self, group):
        return Step(body=Block(tuple(group)), direction=self._group_direction(group))

    def _group_direction(self, group):
        directions = self._group_directions(group)
        if not directions:
            return None
        [direction] = directions
        return direction

    def _group_directions(self, group):
        return {d for n in group for d in self.declaration_directions(n)}
