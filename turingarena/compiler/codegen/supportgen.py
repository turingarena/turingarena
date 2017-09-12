from abc import abstractmethod


class AbstractSupportGenerator:

    def __init__(self, task, interface, dest_dir):
        self.task = task
        self.interface = interface
        self.dest_dir = dest_dir

    @abstractmethod
    def generate(self):
        pass