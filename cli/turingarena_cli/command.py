from abc import abstractmethod, ABC


class Command(ABC):
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def run(self):
        pass
