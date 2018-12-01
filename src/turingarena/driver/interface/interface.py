import logging
from collections import namedtuple

logger = logging.getLogger(__name__)


class Interface(namedtuple("Interface", [
    "constants",
    "methods",
    "main_block",
])):
    __slots__ = []
