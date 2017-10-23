from abc import abstractmethod


class AbstractProxyGenerator:
    def __init__(self, task, dest_dir):
        self.task = task
        self.dest_dir = dest_dir

    @abstractmethod
    def generate(self):
        pass


class AbstractInterfaceProxyGenerator:
    def __init__(self, interface, *, package_dir):
        self.package_dir = package_dir
        self.interface = interface

    @abstractmethod
    def generate(self):
        pass
