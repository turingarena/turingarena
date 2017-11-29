import re


def module_to_python_package(qualifier, name):
    return ".".join(python_module_parts(qualifier, name))


def python_module_parts(qualifier, name):
    parts = parse_module_name(name)
    return [MODULES_PACKAGE, qualifier, *parts]


part_regex = re.compile("^[a-z][a-z_]*$")


def parse_module_name(protocol_name):
    parts = protocol_name.split(".")
    assert len(parts) >= 1
    assert all(
        part_regex.fullmatch(part) is not None
        for part in parts
    )
    return parts


MODULES_PACKAGE = "turingarena_modules"
PROTOCOL_QUALIFIER = "protocol"


def compile_protocol(protocol_def):
    from turingarena.protocol.model.model import Protocol
    from turingarena.protocol.parser import parse_protocol
    ast = parse_protocol(protocol_def)
    return Protocol.compile(ast=ast)