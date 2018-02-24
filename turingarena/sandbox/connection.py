import logging

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeChannelDescriptor, PipeDescriptor

logger = logging.getLogger(__name__)


class SandboxConnection(ImmutableObject):
    __slots__ = ["request", "response"]


SANDBOX_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        request=PipeDescriptor("request.pipe", ("w", "r")),
        response=PipeDescriptor("response.pipe", ("r", "w")),
    ),
)

SANDBOX_PROCESS_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        downward=PipeDescriptor("downward.pipe", ("w", "r")),
        upward=PipeDescriptor("upward.pipe", ("r", "w")),
    ),
)

SANDBOX_WAIT_BARRIER = PipeChannelDescriptor(
    pipes=dict(
        wait_barrier=PipeDescriptor("wait_barrier.pipe", ("w", "r")),
    ),
)


class SandboxProcessConnection(ImmutableObject):
    __slots__ = ["downward", "upward"]
