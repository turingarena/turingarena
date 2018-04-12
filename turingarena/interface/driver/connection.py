from turingarena.pipeboundary import PipeDescriptor, PipeSynchronousQueueDescriptor


DRIVER_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        sandbox_process_dir=PipeDescriptor("sandbox_process_dir.pipe", ("w", "r")),
        interface_name=PipeDescriptor("interface_name.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        driver_process_dir=PipeDescriptor("driver_process_dir.pipe", ("r", "w")),
    ),
)

DRIVER_PROCESS_QUEUE = PipeSynchronousQueueDescriptor(
    request_pipes=dict(
        request=PipeDescriptor("request.pipe", ("w", "r")),
    ),
    response_pipes=dict(
        driver_error=PipeDescriptor("driver_error.pipe", ("r", "w")),
        sandbox_error=PipeDescriptor("sandbox_error.pipe", ("r", "w")),
        response=PipeDescriptor("response.pipe", ("r", "w")),
    ),
)
