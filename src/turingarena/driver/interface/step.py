from collections import namedtuple

from turingarena.driver.interface.seq import SequenceNode


class Step(SequenceNode, namedtuple("Step", ["children", "direction"])):
    __slots__ = []
