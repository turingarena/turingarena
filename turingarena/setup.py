from turingarena.protocol.module import install_protocol_from_source


def turingarena_setup(*, source_dir=".", protocols):
    for protocol_name in protocols:
        install_protocol_from_source(source_dir, protocol_name)
