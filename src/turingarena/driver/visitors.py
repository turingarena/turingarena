class StatementVisitor:
    __slots__ = []

    def statement(self, statement):
        ans = getattr(self, f"{statement.statement_type}_statement")(statement)
        if ans is NotImplemented:
            ans = self.any_statement(statement)
        if ans is NotImplemented:
            raise NotImplementedError
        return ans

    def any_statement(self, statement):
        return NotImplemented

    def read_statement(self, read_statement):
        return NotImplemented

    def write_statement(self, write_statement):
        return NotImplemented

    def checkpoint_statement(self, checkpoint_statement):
        return NotImplemented

    def break_statement(self, break_statement):
        return NotImplemented

    def exit_statement(self, exit_statement):
        return NotImplemented

    def return_statement(self, return_statement):
        return NotImplemented

    def call_statement(self, call_statement):
        return NotImplemented

    def if_statement(self, if_statement):
        return NotImplemented

    def switch_statement(self, switch_statement):
        return NotImplemented

    def for_statement(self, for_statement):
        return NotImplemented

    def loop_statement(self, loop_statement):
        return NotImplemented


class ExpressionVisitor:
    __slots__ = []

    def expression(self, e):
        ans = getattr(self, f"{e.expression_type}_expression")(e)
        if ans is NotImplemented:
            ans = self.any_expression(e)
        if ans is NotImplemented:
            raise NotImplementedError
        return ans

    def any_expression(self, e):
        return NotImplemented

    def subscript_expression(self, e):
        return NotImplemented

    def reference_expression(self, e):
        return NotImplemented

    def int_literal_expression(self, e):
        return NotImplemented
