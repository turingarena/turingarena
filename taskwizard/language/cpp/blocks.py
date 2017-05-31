from taskwizard.generation.blocks import BlockItemVisitor
from taskwizard.language.cpp.declarations import generate_declaration
from taskwizard.language.cpp.statements import generate_statement


class BlockItemGenerator(BlockItemVisitor):

    def __init__(self, external_scope):
        self.scope = dict(external_scope)

    def visit_declaration(self, declaration):
        yield from generate_declaration(declaration, self.scope)

    def visit_statement(self, statement):
        yield from generate_statement(statement, self.scope)


def generate_block(block, external_scope):
    generator = BlockItemGenerator(external_scope)
    for item in block.block_items:
        yield from generator.visit(item)
