import logging
from collections import namedtuple

logger = logging.getLogger(__name__)


class StaticGlobalContext(namedtuple("StaticGlobalContext", [
    "methods",
])):
    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def create_local(self):
        return StaticLocalContext(
            global_context=self,
            outer_context=None,
            locally_defined_variables=(),
            index_variables=(),
            in_loop=False,
            has_break=False,
        )


class StaticLocalContext(namedtuple("StaticLocalContext", [
    "global_context",
    "outer_context",
    "locally_defined_variables",
    "index_variables",
    "in_loop",
    "has_break",
])):
    def with_variables(self, variables):
        return self._replace(
            locally_defined_variables=self.locally_defined_variables + tuple(variables)
        )

    @property
    def variables(self):
        return self.outer_variables + self.locally_defined_variables

    @property
    def variable_mapping(self):
        return {v.name: v for v in self.variables}

    @property
    def outer_variables(self):
        return self.outer_context.variables if self.outer_context else ()

    def with_index_variable(self, variable):
        return self.with_variables((variable.variable,))._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)

    def with_break(self, has_break):
        return self._replace(has_break=has_break)

    def create_inner(self):
        return self._replace(
            outer_context=self,
            locally_defined_variables=(),
            has_break=False
        )


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass
