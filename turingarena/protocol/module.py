import logging
import os
import pickle

from turingarena.modules import parse_module_name

logger = logging.getLogger(__name__)

PROTOCOL_QUALIFIER = "protocol"


class ProtocolSource:
    def __init__(self, source_text, **kwargs):
        from turingarena.protocol.model.model import ProtocolDefinition
        from turingarena.protocol.parser import parse_protocol

        ast = parse_protocol(source_text, **kwargs)

        self.source_text = source_text
        self.definition = ProtocolDefinition.compile(ast=ast)

    def generate(self, *, name, dest_dir):
        parts = parse_module_name(name)
        module_dir = os.path.join(
            dest_dir,
            *parts[:],
        )
        os.makedirs(module_dir, exist_ok=True)

        dest_source_filename = os.path.join(module_dir, "_source.tap")
        with open(dest_source_filename, "w") as f:
            f.write(self.source_text)

        with open(os.path.join(module_dir, "_definition.pickle"), "wb") as f:
            pickle.dump(self.definition, f)

        from turingarena.protocol.skeleton import generate_skeleton
        generate_skeleton(self.definition, dest_dir=os.path.join(module_dir, "_skeletons"))


def locate_protocol_dir(protocol):
    parts = parse_module_name(protocol)
    for lookup_dir in os.environ.get("TURINGARENA_INTERFACE_PATH", "").split(":") + ["."]:
        logger.debug(f"looking for {protocol} in {lookup_dir}")
        path = os.path.join(
            lookup_dir,
            *parts[:]
        )
        if os.path.isdir(path):
            return path
    raise ValueError(f"unable to load protocol {protocol}")


def load_interface_definition(interface):
    protocol, interface_name = interface.split(":")
    protocol_dir = locate_protocol_dir(protocol)

    with open(os.path.join(protocol_dir, "_definition.pickle"), "rb") as f:
        protocol_definition = pickle.load(f)
    return protocol_definition.body.scope.interfaces[interface_name]


def load_interface_signature(interface):
    return load_interface_definition(interface).signature
