from abc import abstractmethod


class BlockItemVisitor:

    def visit(self, item):
        if item.parseinfo.rule.endswith("statement"):
            return self.visit_statement(item)
        if item.parseinfo.rule.endswith("declaration"):
            return self.visit_declaration(item)

    @abstractmethod
    def visit_statement(self, statement):
        pass

    @abstractmethod
    def visit_declaration(self, declaration):
        pass
