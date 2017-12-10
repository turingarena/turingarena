import importlib

import pkg_resources

from turingarena.common import ImmutableObject
from turingarena.modules import module_to_python_package


class ProtocolModule(ImmutableObject):
    __slots__ = [
        "name",
        "definition",
    ]


def load_protocol(protocol_name):
    resource = module_to_python_package(PROTOCOL_QUALIFIER, protocol_name), "_source.tap"
    protocol_text = pkg_resources.resource_string(*resource).decode()

    return compile_protocol(protocol_text)


def load_interface_signature(protocol_name, interface_name):
    proxy_module = importlib.import_module(
        module_to_python_package(PROTOCOL_QUALIFIER, protocol_name) + "._proxy",
    )
    return getattr(proxy_module, interface_name)


PROTOCOL_QUALIFIER = "protocol"


def compile_protocol(text, **kwargs):
    from turingarena.protocol.model.model import ProtocolDefinition
    from turingarena.protocol.parser import parse_protocol
    ast = parse_protocol(text, **kwargs)
    return ProtocolDefinition.compile(ast=ast)