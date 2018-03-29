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
    "message"
])):
    @staticmethod
    def create_message(message):
        return Diagnostic(message=message)


class VariableNotInitializedError(InterfaceError):
    """
    Raised when a variable is used before it's initialized
    """


class GlobalVariableNotInitializedError(VariableNotInitializedError):
    """
    Raised when a global variable is used before it's initialized
    """


class VariableNotAllocatedError(InterfaceError):
    """
    Raised when a variable is used before it's allocated
    """


class VariableNotDeclaredError(InterfaceError):
    """
    Raised when a variable is not defined in a scope
    """


class FunctionCallError(InterfaceError):
    """
    Raised when there is an error in a function call
    """


class FunctionNotDeclaredError(FunctionCallError):
    """
    Raised when you try to call a function that was not defined
    """


class CommunicationBroken(Exception):
    """
    Raised when the communication with a process is interrupted.
    """


