import logging
from collections import namedtuple

from turingarena_impl.interface.variables import Reference

logger = logging.getLogger(__name__)


class InterfaceContext(namedtuple("InterfaceContext", [
    "methods",
])):
    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def main_block_context(self):
        return StatementContext(
            global_context=self,
            declared_references=(),
            resolved_references=(),
            index_variables=(),
            in_loop=False,
        )


class StatementContext(namedtuple("StatementContext", [
    "global_context",
    "declared_references",
    "resolved_references",
    "index_variables",
    "in_loop",
])):
    def with_declared_references(self, references):
        references = self._check_references(references)
        return self._replace(
            declared_references=self.declared_references + references
        )

    def with_resolved_references(self, references):
        references = self._check_references(references)
        return self._replace(
            resolved_references=self.resolved_references + references
        )

    def _check_references(self, references):
        references = tuple(references)
        assert all(isinstance(r, Reference) for r in references)
        return references

    @property
    def declared_variables(self):
        return [
            r.variable
            for r in self.declared_references
        ]

    @property
    def variable_mapping(self):
        return {v.name: v for v in self.declared_variables}

    def with_index_variable(self, variable):
        return self._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass
