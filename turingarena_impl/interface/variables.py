from collections import namedtuple


class Variable(namedtuple("Variable", ["name", "value_type"])):
    @property
    def metadata(self):
        return dict(
            name=self.name,
            type=self.value_type.metadata,
        )
