import os

from turingarena.driver.client.program import Program


def run_algorithm(source_path, interface_path=None):
    if interface_path is None:
        interface_path = os.path.abspath("interface.txt")

    source_path = os.path.abspath(source_path)

    return Program(
        source_path=source_path,
        interface_path=interface_path,
    ).run()
