import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure

logger = logging.getLogger(__name__)


class Loop(namedtuple("Loop", ["body"]), ControlStructure, IntermediateNode):
    __slots__ = []

    def _get_bodies(self):
        yield self.body


class Break(namedtuple("Break", []), IntermediateNode):
    __slots__ = []
