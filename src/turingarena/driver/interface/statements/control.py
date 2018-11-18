from abc import abstractmethod


class ControlStructure:
    @property
    def bodies(self):
        return tuple(self._get_bodies())

    @abstractmethod
    def _get_bodies(self):
        pass
