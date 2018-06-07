from collections import namedtuple

from turingarena.pipeboundary import PipeDescriptor, PipeSynchronousQueueDescriptor, PipeChannelDescriptor

DriverProcessConnection = namedtuple("DriverProcessConnection", ["downward", "upward"])

DRIVER_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        sandbox_process_dir=PipeDescriptor("sandbox_process_dir.pipe", ("w", "r")),
        interface_name=PipeDescriptor("interface_name.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        driver_process_dir=PipeDescriptor("driver_process_dir.pipe", ("r", "w")),
    ),
)

DRIVER_PROCESS_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        downward=PipeDescriptor("downward.pipe", ("w", "r")),
        upward=PipeDescriptor("upward.pipe", ("r", "w")),
    ),
)
