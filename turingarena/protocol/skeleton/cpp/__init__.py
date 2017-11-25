import os

from turingarena.common import write_to_file
from turingarena.protocol.skeleton.cpp.statements import generate_block, generate_statement, build_declaration, \
    build_parameter


def generate_main_file(interface):
    yield "#include <cstdio>"
    for statement in interface.body.statements:
        yield
        yield from generate_statement(statement, interface=interface)


def generate_skeleton(*, protocol, interface, dest_dir):
    main_file = open(os.path.join(dest_dir, "main.cpp"), "w")
    include_file = open(os.path.join(dest_dir, "main.h"), "w")
    write_to_file(generate_main_file(interface), main_file)
