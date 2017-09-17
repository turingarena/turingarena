import os

import tatsu
from tatsu.ast import AST

from turingarena.interfaces.grammar import grammar_ebnf


def parse(*args, **kwargs):
    grammar = tatsu.compile(grammar_ebnf)
    return grammar.parse(*args, **kwargs, asmodel=False, semantics=Semantics(), parseinfo=True)


class TaskParser:
    def __init__(self, definition_dir):
        self.definition_dir = definition_dir
        self.task_file_path = os.path.join(definition_dir, "interfaces.txt")

    def parse(self):
        return parse(open(self.task_file_path).read(), rule="unit")


class Semantics:
    def _default(self, ast, *args, **kwargs):
        if isinstance(ast, AST):
            return AbstractSyntaxNode(ast, *args, **kwargs)
        else:
            return ast


class AbstractSyntaxNode:
    def __init__(self, ast, *args, **kwargs):
        self.parseinfo = None
        for key, value in ast.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._arguments = args

    def info(self):
        return self.parseinfo.text_lines()[0].strip()

    def accept(self, visitor):
        method_name = "visit_%s" % self.parseinfo.rule
        if hasattr(visitor, method_name):
            method = getattr(visitor, method_name)
        elif hasattr(visitor, "visit_default"):
            method = visitor.visit_default
        else:
            raise NotImplementedError("unable to visit %s" % self.parseinfo.rule)
        return method(self)
