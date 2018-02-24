import logging

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeChannelDescriptor, PipeDescriptor, PipeSynchronousQueueDescriptor

logger = logging.getLogger(__name__)


class SandboxConnection(ImmutableObject):
    __slots__ = ["request", "response"]


SANDBOX_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        algorithm_dir=PipeDescriptor("algorithm_dir.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        sandbox_process_dir=PipeDescriptor("sandbox_process_dir.pipe", ("r", "w")),
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
