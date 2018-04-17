class AlgorithmRuntimeError(Exception):
    pass


class CompilationFailed(Exception):
    pass


class TimeLimitExceeded(AlgorithmRuntimeError):
    pass


class MemoryLimitExceeded(AlgorithmRuntimeError):
    pass
