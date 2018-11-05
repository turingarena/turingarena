class InterfaceExit(BaseException):
    pass


class InterfaceError(Exception):
    pass


class AlgorithmError(Exception):
    def __init__(self, process, message):
        self.process = process
        self.message = message


class AlgorithmRuntimeError(AlgorithmError):
    pass


class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass
