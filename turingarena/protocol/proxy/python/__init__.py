import os

from turingarena.protocol.codegen.utils import write_to_file
from turingarena.protocol.proxy.common import AbstractProxyGenerator, AbstractInterfaceProxyGenerator


class InterfaceProxyGenerator(AbstractInterfaceProxyGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.module_path = os.path.join(
            self.package_dir,
            self.interface.name + ".py"
        )

        module_file = open(self.module_path, "w")
        write_to_file(self.generate_module(), module_file)

    def generate_module(self):
        yield "from __future__ import print_function"
        yield "from abc import abstractmethod"
        yield
        yield from InterfaceGenerator().generate_interface(self.interface)


class ProxyGenerator(AbstractProxyGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.package_dir = os.path.join(self.dest_dir, "protocol")
        os.mkdir(self.package_dir)

        for interface in self.task.interfaces:
            self.generate_interface(interface)

    def generate_interface(self, interface):
        InterfaceProxyGenerator(interface, package_dir=self.package_dir).generate()
