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
    class Messages():
        VARIABLE_NOT_DECLARED = "variable {} not declared"
        VARIABLE_NOT_INITIALIZED = "variable {} not initialized before use"
        VARIABLE_NOT_ALLOCATED = "variable {} not allocated before use"
        VARIABLE_REDECLARED = "variable {} has been already declared"
        GLOBAL_VARIABLE_NOT_INITIALIZED = "global variable {} not initialized in init block"
        INIT_BLOCK_MISSING = "global variables declared but init block is missing"
        NOT_ARRAY_TYPE = "argument {} type is not array"
        MISSING_FLUSH = "missing flush between write and read instructions"
        FUNCTION_NOT_DECLARED = "function {} not declared"
        FUNCTION_DOES_NOT_RETURN_VALUE = "function {} does not return a value"
        RETURN_TYPE_MUST_BE_SCALAR = "return type must be a scalar"
        CALL_WRONG_ARGS_NUMBER = "function {} expects {} argument(s), got {}"
        CALL_WRONG_ARGS_TYPE = "wrong type for argument {} of function {}: expected {}, got {}"
        CALL_NO_RETURN_EXPRESSION = "function {} returns {}, but no return expression given"
        CALL_WRONG_RETURN_EXPRESSION = "function {} returns {}, but return expression is {}"
        CALLBACK_PARAMETERS_MUST_BE_SCALARS = "callback parameters must be scalars"
        ARRAY_INDEX_NOT_VALID = "array index {} is not a for index variable"
        ARRAY_INDEX_WRONG_ORDER = "array {} indexes are in wrong order"
        ARRAY_INDEX_DIFFERENT_ALLOC = "array {} index {} different from allocated"
        EMPTY_SWITCH_BODY = "switch statement body must contain at least one case"
        UNEXPECTED_BREAK = "break statement should only appear inside loop {} or switch case() {} blocks"
        UNEXPECTED_CONTINUE = "continue should only appear inside loop {} statements"
        UNEXPECTED_RETURN = "return statement should only appear inside a callback declaration"
        INVALID_CASE_EXPRESSION = "case expression must be an int literal"
        CASE_FALLTROUGH = "case must terminate either with a break, continue, return or exit in every possible branch"
        INFINITE_LOOP = "loop must contain at least a break, exit or return statement"
        UNREACHED_STATEMENT = "statement {} is never reached reached"

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
