import logging

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class Algorithm(ImmutableObject):
    __slots__ = [
        "protocol_name",
        "interface_name",
        "source",
        "executable",
    ]
