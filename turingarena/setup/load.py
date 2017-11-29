import importlib
import pkg_resources

from turingarena.setup.common import *


def load_protocol(protocol_name):
    protocol_def = pkg_resources.resource_string(
        module_to_python_package(PROTOCOL_QUALIFIER, protocol_name),
        "_source.tap",
    ).decode()

    return compile_protocol(protocol_def)


def load_interface_signature(protocol_name, interface_name):
    proxy_module = importlib.import_module(
        module_to_python_package(PROTOCOL_QUALIFIER, protocol_name) + "._proxy",
    )
    return getattr(proxy_module, interface_name)