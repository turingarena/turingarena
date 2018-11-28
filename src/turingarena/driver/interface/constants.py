from collections.__init__ import namedtuple


class ConstantDeclaration(namedtuple("ConstantDeclaration", ["variable", "value"])):
    __slots__ = []