from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeDescriptor, PipeChannelDescriptor


class DriverProcessConnection(ImmutableObject):
    __slots__ = ["request", "response"]


DRIVER_PROCESS_CHANNEL = PipeChannelDescriptor(
    pipes=dict(
        request=PipeDescriptor("request.pipe", ("w", "r")),
        response=PipeDescriptor("response.pipe", ("r", "w")),
    ),
)
