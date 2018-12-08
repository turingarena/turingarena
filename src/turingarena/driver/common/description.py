from turingarena.driver.common.expressions import AbstractExpressionCodeGen
from turingarena.driver.common.genutils import LinesGenerator
from turingarena.util.visitor import visitormethod


class TreeDumper(AbstractExpressionCodeGen, LinesGenerator):
    def dump(self, n):
        with self.collect_lines() as lines:
            self._on_dump(n)
        return lines.as_inline()

    @visitormethod
    def _on_dump(self, n):
        pass

    def _on_dump_object(self, n):
        self.line(repr(n))

    def _on_dump_Enum(self, n):
        self.line(str(n))

    def _on_dump_tuple(self, n):
        if len(n) == 0:
            self.line(f"{n.__class__.__name__}()")
            return

        if len(n) == 1:
            self.line(f"{n.__class__.__name__}({self.dump(n[0])})")
            return

        self.line(f"{n.__class__.__name__}(")
        with self.indent():
            if hasattr(n, "_fields"):
                for f in n._fields:
                    self.line(f"{f}={self.dump(getattr(n, f))},")
            else:
                for v in n:
                    self.line(f"{self.dump(v)},")
            self.line(f"# end {n.__class__.__name__}")
        self.line(f")")


class StatementDescriber(AbstractExpressionCodeGen):
    @visitormethod
    def description(self, n):
        pass

    def description_Read(self, n):
        arguments = ", ".join(self.visit(e) for e in n.arguments)
        return f"read {arguments}"

    def description_Write(self, n):
        arguments = ", ".join(self.visit(e) for e in n.arguments)
        return f"write {arguments}"

    def description_Checkpoint(self, n):
        return f"checkpoint"

    def description_Call(self, n):
        if n.return_value is not None:
            return_expr = f"{self.visit(n.return_value)} = "
        else:
            return_expr = f""

        arguments = ", ".join(self.visit(e) for e in n.arguments)

        if n.callbacks:
            callbacks_expr = f" callbacks {{...}}"
        else:
            callbacks_expr = f""

        return f"call {return_expr}{n.method.name}({arguments}){callbacks_expr}"

    def description_Return(self, n):
        v = self.visit(n.value)
        return f"return {v}"

    def description_For(self, n):
        i = self.visit(n.index.variable)
        r = self.visit(n.index.range)
        return f"for {i} to {r} {{...}}"

    def description_Loop(self, n):
        return f"loop {{...}}"

    def description_Break(self, n):
        return f"break"

    def description_If(self, n):
        c = self.visit(n.condition)
        if n.branches.else_body is not None:
            else_expr = f" else {{...}}"
        else:
            else_expr = f""
        return f"if {c} {{...}}{else_expr}"

    def description_Switch(self, n):
        v = self.visit(n.value)
        return f"switch {v} {{...}}"

    def description_Exit(self, n):
        return f"exit"
