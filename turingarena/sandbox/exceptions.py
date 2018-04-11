class AlgorithmRuntimeError(Exception):
    pass


class CompilationFailed(Exception):
    def __init__(self, output=None):
        self.compilation_output = output


class TimeLimitExceeded(AlgorithmRuntimeError):
    pass


class MemoryLimitExceeded(AlgorithmRuntimeError):
    pass
