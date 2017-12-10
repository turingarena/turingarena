def do_generate_proxy(protocol):
    yield "from collections import OrderedDict"
    yield "from turingarena.protocol.model.model import *"
    yield "from turingarena.protocol.model.type_expressions import *"
    yield
    for interface in protocol.body.scope.interfaces.values():
        yield f"{interface.name} = {repr(interface.signature)}"
