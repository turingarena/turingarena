class InterfaceExit(BaseException):
    pass


class ProcessStop(BaseException):
    pass


class InterfaceError(Exception):
    pass


class AlgorithmError(Exception):
    def __init__(self, message, *, process):
        self.process = process
        self.message = message


class AlgorithmRuntimeError(AlgorithmError):
    pass


class AlgorithmLogicError(AlgorithmError):
    pass


class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass
