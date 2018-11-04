import resource


def set_rlimits(
        memory_limit=256 * 1024 * 1024,
):
    resource.setrlimit(
        resource.RLIMIT_CORE,
        (0, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_STACK,
        (resource.RLIM_INFINITY, resource.RLIM_INFINITY),
    )
    if memory_limit is not None:
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_limit, resource.RLIM_INFINITY),
        )
