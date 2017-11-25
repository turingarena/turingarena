import importlib
import pkg_resources
import re

part_regex = re.compile("^[a-z][a-z_]*$")


def parse_protocol_name(protocol_name):
    parts = protocol_name.split(".")
    assert len(parts) >= 1
    assert all(
        part_regex.fullmatch(part) is not None
        for part in parts
    )
    return parts


def load_protocol(protocol_name):
    protocol_def = pkg_resources.resource_string(
        f"turingarena_protocols.{protocol_name}",
        "__init__.tap",
    )

    from turingarena.protocol.model.model import Protocol
    from turingarena.protocol.parser import parse_protocol

    ast = parse_protocol(protocol_def.decode())
    return Protocol.compile(ast=ast)


def load_interface_signature(protocol_name, interface_name):
    proxy_module = importlib.import_module(
        f"turingarena_proxies.{protocol_name}",
    )
    return getattr(proxy_module, interface_name)
