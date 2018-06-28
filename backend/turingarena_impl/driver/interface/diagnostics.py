from collections import namedtuple


class Diagnostic(namedtuple("Diagnostic", [
    "message",
    "parseinfo",
])):
    class Messages:
        VARIABLE_NOT_DECLARED = "variable {} not declared"
        VARIABLE_REUSED = "variable {} already used"
        NOT_ARRAY_TYPE = "argument {} type is not array"
        METHOD_NOT_DECLARED = "method {} not declared"
        METHOD_DOES_NOT_RETURN_VALUE = "method {} (procedure) does not return a value"
        RETURN_TYPE_MUST_BE_SCALAR = "return type must be a scalar"
        CALL_WRONG_ARGS_NUMBER = "method {} expects {} argument(s), got {}"
        CALL_WRONG_ARGS_TYPE = "argument {} of method {}: expected {} dimensions, got {}"
        CALL_NO_RETURN_EXPRESSION = "function call with no return expression given"
        CALL_WRONG_RETURN_EXPRESSION = "method {} (function) returns {}, but return expression is {}"
        CALLBACK_PARAMETERS_MUST_BE_SCALARS = "callback parameters must be scalars"
        WRONG_ARRAY_INDEX = "expected array index {}"
        UNEXPECTED_ARRAY_INDEX = "unexpected array index"
        EMPTY_SWITCH_BODY = "switch statement body must contain at least one case"
        UNEXPECTED_BREAK = "break statement used outside a loop"
        UNEXPECTED_RETURN = "return statement should only appear inside a callback declaration"
        UNREACHABLE_CODE = "unreachable code after break/exit"
        DUPLICATED_CASE_LABEL = "duplicated case label {}"
        UNEXPECTED_CALLBACK = "callback {} not allowed here"
        SWITCH_LABEL_NOT_LITERAL = "switch labels must be integer literals"

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
