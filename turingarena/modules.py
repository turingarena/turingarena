import re

MODULES_PACKAGE = "turingarena_modules"


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
