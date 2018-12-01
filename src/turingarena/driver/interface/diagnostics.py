class Diagnostic(tuple):
    def __new__(cls, **kwargs):
        return super().__new__(cls, [cls] + list(kwargs.items()))

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.message = self.__class__.__doc__.format(**self.__dict__)

    def __str__(self):
        return self.message


class CodeReference(tuple):
    def __new__(cls, ast):
        return super().__new__(cls, (cls, ast.parseinfo))

    @property
    def parseinfo(self):
        return self[1]

    @property
    def line_info(self):
        return self.parseinfo.buffer.line_info(self.parseinfo.pos)

    @property
    def text(self):
        return self.parseinfo.buffer.text[self.parseinfo.pos:self.parseinfo.endpos]


class Location(CodeReference):
    def __str__(self):
        return f"line {self.line_info.line + 1}"


class Snippet(CodeReference):
    def __str__(self):
        return f"'{self.text}'"


# Declarations

class ConstantAlreadyDeclared(Diagnostic):
    """constant {constant} already declared"""


class MethodAlreadyDeclared(Diagnostic):
    """method {method} already declared"""


class CallbackParameterNotScalar(Diagnostic):
    """expecting scalar callback parameter, got {parameter}"""


# Expressions / references

class InvalidSubscript(Diagnostic):
    """cannot subscript {array}, got {index}"""


class InvalidReference(Diagnostic):
    """expecting reference, got {expression}"""


class InvalidIndexForReference(Diagnostic):
    """expecting index {index}, got {expression}"""


class UnexpectedIndexForReference(Diagnostic):
    """no more index expected, got {expression}"""


class ReferenceNotDefined(Diagnostic):
    """reference {expression} not defined"""


class ReferenceAlreadyDefined(Diagnostic):
    """reference {expression} already defined"""


class ReferenceNotUsed(Diagnostic):
    """reference {expression} was never used"""


class ExpressionNotScalar(Diagnostic):
    """expecting a scalar, got {expression}"""


class ExpressionNotLiteral(Diagnostic):
    """expecting a literal, got {expression}"""


# Call

class MethodNotDeclared(Diagnostic):
    """method {name} not declared"""


class InvalidNumberOfArguments(Diagnostic):
    """method {name} expects {n_parameters} parameters, got {n_arguments}"""


class InvalidArgument(Diagnostic):
    __doc__ = (
        """parameter {parameter} of method {name} has {dimensions} dimensions, """
        """got {argument} ({argument_dimensions} dimensions)"""
    )


class IgnoredReturnValue(Diagnostic):
    """function {name} returns a value"""


class NoReturnValue(Diagnostic):
    """procedure {name} does not return a value"""


class CallbackNotDeclared(Diagnostic):
    """method {name} does not declare callback {callback}"""


class CallbackAlreadyImplemented(Diagnostic):
    """callback {name} already implemented"""

class CallbackPrototypeMismatch(Diagnostic):
    """callback {name} does not match declared prototype"""


# Others

class SwitchEmpty(Diagnostic):
    """switch body empty"""


class CaseLabelDuplicated(Diagnostic):
    """duplicated case label {label}"""


class BreakOutsideLoop(Diagnostic):
    """outside loop, got {statement}"""


class ReturnOutsideCallback(Diagnostic):
    """outside callback, got {statement}"""


class DanglingCode(Diagnostic):
    """possibly unreachable after break / exit, got {statement}"""
