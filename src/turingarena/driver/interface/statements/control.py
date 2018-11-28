from abc import abstractmethod

from turingarena.driver.interface.statements.callback import Exit


class ControlStructure:
    @property
    def bodies(self):
        return tuple(self._get_bodies())

    @abstractmethod
    def _get_bodies(self):
        pass


class MainExit(Exit):
    pass