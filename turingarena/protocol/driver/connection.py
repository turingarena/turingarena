from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeDescriptor, PipeChannelDescriptor, PipeSynchronousQueueDescriptor


class DriverProcessConnection(ImmutableObject):
    __slots__ = ["request", "response"]


DRIVER_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        sandbox_process_dir=PipeDescriptor("sandbox_process_dir.pipe", ("w", "r")),
        interface_text=PipeDescriptor("interface.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        driver_process_dir=PipeDescriptor("driver_process_dir.pipe", ("r", "w")),
    ),
)

DRIVER_PROCESS_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        request=PipeDescriptor("request.pipe", ("w", "r")),
        response=PipeDescriptor("response.pipe", ("r", "w")),
    ),
)
