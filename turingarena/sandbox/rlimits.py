import resource


def set_memory_and_time_limits(
        memory_limit=16 * 1024 * 1024,
        time_limit=1,
):
    core_limit = 32 * 1024 * 1024
    resource.setrlimit(
        resource.RLIMIT_CORE,
        (core_limit, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_STACK,
        (resource.RLIM_INFINITY, resource.RLIM_INFINITY),
    )
    if time_limit is not None:
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (time_limit, resource.RLIM_INFINITY),
            # use soft < hard to ensure SIGXCPU is raised instead of SIGKILL
            # see setrlimit(2)
        )
    if memory_limit is not None:
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_limit, resource.RLIM_INFINITY),
        )
