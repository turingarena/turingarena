from collections import namedtuple

from turingarena.pipeboundary import PipeDescriptor, PipeChannelDescriptor, PipeSynchronousQueueDescriptor

DriverProcessConnection = namedtuple("DriverProcessConnection", ["downward", "upward"])
SandboxProcessConnection = namedtuple("SandboxProcessConnection", ["downward", "upward"])

DRIVER_PROCESS_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        downward=PipeDescriptor("driver_downward.pipe", ("w", "r")),
        upward=PipeDescriptor("driver_upward.pipe", ("r", "w")),
    ),
)

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
        status=PipeDescriptor("status.pipe", ("r", "w")),
        time_usage=PipeDescriptor("time_usage.pipe", ("r", "w")),
        memory_usage=PipeDescriptor("memory_usage.pipe", ("r", "w")),
        error=PipeDescriptor("error.pipe", ("r", "w")),
    ),
)
