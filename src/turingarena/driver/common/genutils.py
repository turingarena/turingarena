from abc import abstractmethod
from contextlib import contextmanager


class LineCollector:
    def __init__(self):
        self._lines = []

    def indented_lines(self):
        for indentation, l in self._lines:
            if l is None:
                yield "\n"
            else:
                yield "    " * indentation + l + "\n"

    def add_line(self, indentation, line):
        self._lines.append((indentation, line))

    def _inline_chunks(self):
        for i, (indentation, l) in enumerate(self._lines):
            if i > 0:
                yield "\n"
                if l is not None:
                    yield "    " * indentation
            if l is not None:
                yield l

    def __iter__(self):
        return iter(self.indented_lines())

    def as_inline(self):
        return "".join(self._inline_chunks())

    def as_block(self):
        return "".join(self.indented_lines())


class LinesGenerator:
    def __init__(self):
        self.indentation = 0
        self.collector = None

    @contextmanager
    def collect_lines(self):
        old_collector = self.collector
        self.collector = collector = LineCollector()
        yield collector
        assert self.collector is collector
        self.collector = old_collector

    @contextmanager
    def indent(self):
        self.indentation += 1
        yield
        self.indentation -= 1

    def line(self, line=None):
        self.collector.add_line(self.indentation, line)

    @abstractmethod
    def _on_generate(self, *args, **kwargs):
        pass