from collections import namedtuple


class CompilationContext(namedtuple("Compiler", [
    "constants",
    "methods",
    "in_callback",
    "prev_reference_actions",
    "index_variables",
    "in_loop",
    "expression_type",
    "diagnostics",
])):
    @classmethod
    def create(cls):
        return cls(
            constants=None,
            methods=None,
            in_callback=False,
            prev_reference_actions=None,
            index_variables=None,
            in_loop=None,
            expression_type=None,
            diagnostics=[],
        )

    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def with_index_variable(self, variable):
        return self._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)

    def with_constant(self, declaration):
        return self._replace(constants=self.constants + (declaration,))

    def with_method(self, method):
        return self._replace(methods=self.methods + (method,))

    def with_reference_actions(self, actions):
        actions = tuple(actions)
        assert all(
            a.reference is not None
            for a in actions
        )
        return self._replace(
            prev_reference_actions=self.prev_reference_actions + actions
        )
