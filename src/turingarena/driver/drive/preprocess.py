from turingarena.driver.common.nodes import *
from turingarena.driver.common.transform import TreeTransformer
from turingarena.driver.drive.analysis import ExecutionAnalyzer
from turingarena.driver.drive.nodes import *
from turingarena.util.visitor import visitormethod


class ExecutionPreprocessor(
    TreeTransformer,
    ExecutionAnalyzer,
):
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
            append_nodes = (RequestLookahead(), CallbackEnd(),)
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

    def node_replacement_Checkpoint(self, n):
        yield RequestLookahead()
        yield self.transform(n)

    def node_replacement_Return(self, n):
        yield RequestLookahead()
        yield self.transform(n)

    def node_replacement_Exit(self, n):
        yield RequestLookahead()
        yield self.transform(n)

    def node_replacement_If(self, n):
        yield RequestLookahead()
        yield ValueResolve(n.condition, tuple(
            (request, value)
            for value, branch in zip((1, 0), n.branches)
            for request in (self.first_requests(branch) if branch is not None else (None,))
        ))
        yield self.transform(n)

    def node_replacement_Switch(self, n):
        yield RequestLookahead()
        yield ValueResolve(n.value, tuple(
            (request, case.labels[0].value)
            for case in n.cases
            for request in self.first_requests(case.body)
        ))
        yield self.transform(n)

    def node_replacement_Call(self, n):
        yield RequestLookahead()
        yield CallArgumentsResolve(method=n.method, arguments=n.arguments)
        if n.method.callbacks:
            yield AcceptCallbacks(self.transform_all(n.callbacks))
        yield CallCompleted()
        if n.method.has_return_value:
            yield CallReturn(n.return_value)

    def group_children(self, children):
        group = []
        for node in children:
            # steps cannot have both UPWARD and DOWNWARD phases

            can_be_grouped = self.can_be_grouped(node) and not all(
                phase in self.phases(node)
                for phase in (ExecutionPhase.UPWARD, ExecutionPhase.DOWNWARD)
            )

            can_be_added_to_group = can_be_grouped and not all(
                phase in self._group_phases(group + [node])
                for phase in (ExecutionPhase.UPWARD, ExecutionPhase.DOWNWARD)
            )

            if can_be_added_to_group:
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
        return Step(body=Block(tuple(group)), phases=self._group_phases(group))

    def _group_phases(self, group):
        return {d for n in group for d in self.phases(n)}
