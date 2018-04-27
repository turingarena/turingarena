import logging
from collections import namedtuple

from turingarena.pipeboundary import PipeChannelDescriptor, PipeDescriptor, PipeSynchronousQueueDescriptor

logger = logging.getLogger(__name__)

SandboxConnection = namedtuple("SandboxConnection", ["request", "response"])
SandboxProcessConnection = namedtuple("SandboxProcessConnection", ["downward", "upward"])

SANDBOX_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        language_name=PipeDescriptor("language_name.pipe", ("w", "r")),
        source_name=PipeDescriptor("source_name.pipe", ("w", "r")),
        interface_name=PipeDescriptor("interface_name.pipe", ("w", "r")),
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

SANDBOX_REQUEST_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        wait=PipeDescriptor("wait.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        error=PipeDescriptor("error.pipe", ("r", "w")),
        time_usage=PipeDescriptor("time_usage.pipe", ("r", "w")),
        memory_usage=PipeDescriptor("memory_usage.pipe", ("r", "w")),
    ),
)
