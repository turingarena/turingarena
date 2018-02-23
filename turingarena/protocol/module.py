import importlib
import os
import pickle

import pkg_resources

from turingarena.modules import module_to_python_package, prepare_module_dir

PROTOCOL_QUALIFIER = "protocol"


class ProtocolSource:
    def __init__(self, source_text, **kwargs):
        from turingarena.protocol.model.model import ProtocolDefinition
        from turingarena.protocol.parser import parse_protocol

        ast = parse_protocol(source_text, **kwargs)

        self.source_text = source_text
        self.definition = ProtocolDefinition.compile(ast=ast)

    def generate(self, *, name, dest_dir):
        module_dir = prepare_module_dir(dest_dir, PROTOCOL_QUALIFIER, name)

        dest_source_filename = os.path.join(module_dir, "_source.tap")
        with open(dest_source_filename, "w") as f:
            f.write(self.source_text)

        with open(os.path.join(module_dir, "_definition.pickle"), "wb") as f:
            pickle.dump(self.definition, f)

        from turingarena.protocol.proxy.python import generate_proxy
        from turingarena.protocol.skeleton import generate_skeleton

        generate_proxy(module_dir, self.definition)
        generate_skeleton(self.definition, dest_dir=os.path.join(module_dir, "_skeletons"))


def load_interface_definition(interface):
    protocol, interface_name = interface.split(":")
    module = module_to_python_package(PROTOCOL_QUALIFIER, protocol)
    path = pkg_resources.resource_filename(module, "_definition.pickle")
    with open(path, "rb") as f:
        protocol_definition = pickle.load(f)
    return protocol_definition.body.scope.interfaces[interface_name]


def load_interface_signature(interface):
    protocol, interface_name = interface.split(":")
    proxy_module = importlib.import_module(
        module_to_python_package(PROTOCOL_QUALIFIER, protocol) + "._proxy",
    )
    return getattr(proxy_module, interface_name)
