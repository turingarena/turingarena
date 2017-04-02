{% import "macro.j2" as macro %}

{{ macro.generate_protocol_header(interface.functions.values(), interface.callback_functions.values()) }}

