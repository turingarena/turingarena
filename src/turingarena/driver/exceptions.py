class InterfaceExit(BaseException):
    pass


class InterfaceError(Exception):
    pass


class AlgorithmError(Exception):
    def __init__(self, process, message, info):
        self.process = process
        self.message = message
        self.info = info


class AlgorithmRuntimeError(AlgorithmError):
    pass


class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass
