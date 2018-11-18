from collections import namedtuple
from typing import Optional

from turingarena.driver.interface.variables import Reference, Variable, ReferenceStatus
from turingarena.util.visitor import visitormethod


class ExpressionAnalyzer(namedtuple("ExpressionAnalyzer", ["context"])):
    @visitormethod
    def variable(self, e) -> Optional[Variable]:
        pass

    def variable_VariableReference(self, e):
        return self.context.variable_mapping.get(e.variable_name)

    def variable_Expression(self, e):
        return None

    @visitormethod
    def dimensions(self, e) -> int:
        pass

    def dimensions_Literal(self, e):
        return 0

    def dimensions_VariableReference(self, e):
        return self.variable(e).dimensions

    def dimensions_Subscript(self, e):
        array_dimensions = self.dimensions(e.array)
        if array_dimensions < 1:
            # not an array, fix
            return 0
        return array_dimensions - 1

    @visitormethod
    def reference(self, e) -> Optional[Reference]:
        pass

    def reference_VariableReference(self, e):
        variable = self.variable(e)
        if variable is not None:
            return variable.as_reference()

    def reference_Subscript(self, e):
        array_reference = self.reference(e.array)
        if array_reference is not None:
            return array_reference._replace(
                index_count=array_reference.index_count + 1,
            )

    def reference_Expression(self, e):
        return None

    def declared_reference(self, e, dimensions=0) -> Optional[Reference]:
        return self._declared_reference(e, dimensions)

    @visitormethod
    def _declared_reference(self, e, dimensions):
        pass

    def _declared_reference_VariableReference(self, e, dimensions):
        return Variable(name=e.variable_name, dimensions=dimensions).as_reference()

    def _declared_reference_Subscript(self, e, dimensions):
        array_reference = self.declared_reference(e.array, dimensions + 1)
        if array_reference is not None:
            return array_reference._replace(
                index_count=array_reference.index_count + 1,
            )

    def _declared_reference_Expression(self, e):
        return None

    @visitormethod
    def is_resolved(self, e) -> bool:
        pass

    def is_resolved_Literal(self, e):
        return True

    def is_resolved_VariableReference(self, e):
        return self.reference(e) in self.context.get_references(ReferenceStatus.RESOLVED)

    def is_resolved_Subscript(self, e):
        return (
                self.reference(e) in self.context.get_references(ReferenceStatus.RESOLVED)
                or self.is_resolved(e.array)
        )
