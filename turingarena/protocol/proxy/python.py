import os

from turingarena.common import write_to_file


def _do_generate_proxy(protocol):
    yield "from collections import OrderedDict"
    yield "from turingarena.protocol.model.model import *"
    yield "from turingarena.protocol.model.type_expressions import *"
    yield
    for interface in protocol.body.scope.interfaces.values():
        yield f"{interface.name} = {repr(interface.signature)}"


def generate_proxy(module_dir, protocol):
    with open(os.path.join(module_dir, "_proxy.py"), "w") as proxy_module_file:
        write_to_file(_do_generate_proxy(protocol), proxy_module_file)
