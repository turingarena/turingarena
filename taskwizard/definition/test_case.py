from taskwizard.definition.declarations import named_definitions


class TestCase:

    def __init__(self, ast):
        self.name = ast.name
        self.phases = named_definitions(ast.phases)


class TestPhase:

    def __init__(self, ast):
        self.name = ast.name
        self.driver_name = ast.driver_name
        self.slots = named_definitions(ast.slots)


class TestPhaseSlot:

    def __init__(self, ast):
        self.name = ast.name
        self.interface_name = ast.interface_name
