from collections import namedtuple

from turingarena.driver.compile.context import CompilationContext
from turingarena.driver.compile.diagnostics import *
from turingarena.util.visitor import visitormethod


class CompileAnalyzer(CompilationContext):
    @property
    def reference_definitions(self):
        return {
            a.reference: a
            for a in self.prev_reference_actions
            if isinstance(a, ReferenceDefinition)
        }

    @visitormethod
    def dimensions(self, e) -> int:
        pass

    def dimensions_IntLiteral(self, e):
        return 0

    def dimensions_Variable(self, e):
        try:
            return self.reference_definitions[e].dimensions
        except KeyError:
            return 0

    def dimensions_Subscript(self, e):
        try:
            return self.reference_definitions[e].dimensions
        except KeyError:
            array_dimensions = self.dimensions(e.array)
            if array_dimensions < 1:
                self.error(InvalidSubscript(array="<TODO>", index="<TODO>"))
                return 0
            return array_dimensions - 1

    @visitormethod
    def is_defined(self, e) -> bool:
        pass

    def is_defined_IntLiteral(self, e):
        return True

    def is_defined_Variable(self, e):
        return e in self.reference_definitions

    def is_defined_Subscript(self, e):
        return (
                e in self.reference_definitions
                or self.is_defined(e.array)
        )


ReferenceDefinition = namedtuple("ReferenceDefinition", ["reference", "dimensions"])
ReferenceResolution = namedtuple("ReferenceResolution", ["reference"])
