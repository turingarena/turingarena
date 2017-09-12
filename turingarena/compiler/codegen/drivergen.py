from abc import abstractmethod


class AbstractDriverGenerator:

    def __init__(self, task, dest_dir):
        self.task = task
        self.dest_dir = dest_dir

    @abstractmethod
    def generate(self):
        pass


class AbstractInterfaceDriverGenerator:

    def __init__(self, driver_generator, interface):
        self.driver_generator = driver_generator
        self.interface = interface

    @abstractmethod
    def generate(self):
        pass


