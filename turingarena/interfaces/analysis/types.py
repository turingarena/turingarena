class ScalarType:
    def __init__(self, base):
        self.base = base

    def accept(self, visitor):
        return visitor.visit_scalar_type(self)
