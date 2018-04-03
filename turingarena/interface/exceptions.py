from collections import namedtuple


class InterfaceExit(Exception):
    pass


class InterfaceError(Exception):
    def __init__(self, message, *, parseinfo=None):
        self.message = message
        self.parseinfo = parseinfo

    def line_info(self):
        return [
            self.parseinfo.buffer.line_info(p)
            for p in (self.parseinfo.pos, self.parseinfo.endpos)
        ]

    def get_user_message(self):
        lineinfo, endlineinfo = self.line_info()
        # lines are zero-based-numbered
        return f"{lineinfo.filename}:{lineinfo.line+1}:{lineinfo.col+1}: {self.message}"


class Diagnostic(namedtuple("Diagnostic", [
    "message",
    "parseinfo",
])):
    class Messages:
        VARIABLE_NOT_DECLARED = "variable {} not declared"
        VARIABLE_NOT_INITIALIZED = "variable {} used before initialization"
        VARIABLE_NOT_ALLOCATED = "variable {} used before allocation"
        VARIABLE_REDECLARED = "variable {} redeclared"
        GLOBAL_VARIABLE_NOT_INITIALIZED = "global variable {} not initialized in init block"
        INIT_BLOCK_MISSING = "global variables declared but missing init block"
        NOT_ARRAY_TYPE = "Argument {} is not an array type"
        MISSING_FLUSH = "missing flush between write and read instructions"
        FUNCTION_NOT_DECLARED = "function {} not declared"
        CALL_WRONG_ARGS_NUMBER = "function {} expects {} argument(s), got {}"
        CALL_WRONG_ARGS_TYPE = "argument {} of function {}: expected {}, got {}"
        CALL_NO_RETURN_EXPRESSION = "function {} returns {}, but no return expression given"
        CALL_WRONG_RETURN_EXPRESSION = "function {} returns {}, but return expression is {}"
        FUNCTION_DOES_NOT_RETURN_VALUE = "function {} does not return a value"
        CALLBACK_PARAMETERS_MUST_BE_SCALARS = "callback parameters must be scalars"
        RETURN_TYPE_MUST_BE_SCALAR = "return type must be a scalar"

    @staticmethod
    def build_message(msg, *args):
        return msg.format(*args)

    def __new__(cls, msg, *args, **kwargs):
        return super().__new__(
            cls,
            message=cls.build_message(msg, *args),
            **kwargs
        )

    @property
    def line_info(self):
        return self.parseinfo.buffer.line_info(self.parseinfo.pos)

    def __str__(self):
        lineinfo = self.line_info
        return f"line {lineinfo.line + 1}: {self.message}"


class CommunicationBroken(Exception):
    """
    Raised when the communication with a process is interrupted.
    """
