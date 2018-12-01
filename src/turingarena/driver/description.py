from turingarena.driver.expressions import AbstractExpressionCodeGen
from turingarena.driver.genutils import LinesGenerator
from turingarena.util.visitor import visitormethod


class TreeDumper(AbstractExpressionCodeGen, LinesGenerator):
    def description(self, n):
        with self.collect_lines() as lines:
            self.describe(n)
        return lines.as_inline()

    @visitormethod
    def describe(self, n):
        pass

    def describe_object(self, n):
        self.line(str(n))

    def describe_tuple(self, n):
        if len(n) == 0:
            self.line(f"{n.__class__.__name__}()")
            return

        self.line(f"{n.__class__.__name__}(")
        with self.indent():
            if hasattr(n, "_fields"):
                for f in n._fields:
                    self.line(f"{f}={self.description(getattr(n, f))},")
            else:
                for v in n:
                    self.line(f"{self.description(v)},")
        self.line(")")
