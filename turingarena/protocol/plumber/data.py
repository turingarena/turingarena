from turingarena.protocol.types import scalar


class Frame:
    def __init__(self, parent, scope):
        self.parent = parent
        self.delegate = {
            name: Var(scope[ns, name].type, name)
            for ns, name in scope.locals()
            if ns == "var"
        }

    def __getitem__(self, key):
        try:
            return self.delegate[key]
        except KeyError:
            if self.parent:
                return self.parent[key]
            else:
                raise


class Var:
    def __init__(self, type_descriptor, name):
        self.type_descriptor = type_descriptor
        self.name = name
        self.value = self.instanciate()

    def instanciate(self):
        if isinstance(self.type_descriptor, scalar):
            return self.type_descriptor.base_type()
        if isinstance(self.type_descriptor, scalar):
            return None
        raise AssertionError()

    def get_value(self):
        pass


def evaluate_expression(expression, *, frame):
    evaluators = {
        "variable": lambda: frame[expression.variable_name].get_value(),
        "int_literal": lambda: expression.int_value,
        "bool_literal": lambda: expression.bool_value,
        "subscript": lambda: evaluate_expression(expression.array, frame=frame)[
            evaluate_expression(expression.index, frame=frame)
        ]
    }
    return evaluators[expression.expression_type]()
