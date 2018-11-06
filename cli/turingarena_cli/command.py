from abc import abstractmethod, ABC


class Command(ABC):
    def __init__(self, args, cwd):
        self.args = args
        self.cwd = cwd

    @abstractmethod
    def run(self):
        pass
