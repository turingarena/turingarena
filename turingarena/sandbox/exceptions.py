class AlgorithmRuntimeError(Exception):
    def __init__(self, message, stacktrace=None):
        self.message = message
        self.stacktrace = stacktrace


class CompilationFailed(Exception):
    pass
