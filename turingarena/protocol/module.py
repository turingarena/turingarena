import logging
import os
import pickle

from turingarena.modules import parse_module_name

logger = logging.getLogger(__name__)

PROTOCOL_QUALIFIER = "protocol"


class InterfaceSource:
    def __init__(self, source_text, **kwargs):
        from turingarena.protocol.model.model import InterfaceDefinition
        from turingarena.protocol.parser import parse_protocol

        ast = parse_protocol(source_text, **kwargs)

        self.source_text = source_text
        self.definition = InterfaceDefinition.compile(
            ast=ast,
        )

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


def locate_interface_dir(interface):
    parts = parse_module_name(interface)
    for lookup_dir in os.environ.get("TURINGARENA_INTERFACE_PATH", "").split(":") + ["."]:
        logger.debug(f"looking for {interface} in {lookup_dir}")
        path = os.path.join(
            lookup_dir,
            *parts[:]
        )
        if os.path.isdir(path):
            return path
    raise ValueError(f"unable to load protocol {interface}")


def load_interface_definition(interface):
    interface_dir = locate_interface_dir(interface)

    with open(os.path.join(interface_dir, "_definition.pickle"), "rb") as f:
        return pickle.load(f)


def load_interface_signature(interface):
    return load_interface_definition(interface).signature
