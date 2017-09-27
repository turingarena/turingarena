import os

import tatsu
from tatsu.ast import AST

from turingarena.interfaces.grammar import grammar_ebnf

import logging
logger = logging.getLogger(__name__)


def parse(*args, **kwargs):
    return tatsu.parse(grammar_ebnf, *args, **kwargs, asmodel=False, semantics=Semantics(), parseinfo=True)


def parse_interfaces_file(filename):
    logger.info("Parsing interfaces file %s", filename)
    return parse(open(filename).read(), rule="unit")


class Semantics:
    def _default(self, ast, *args, **kwargs):
        if isinstance(ast, AST):
            node = AbstractSyntaxNode(ast, *args, **kwargs)
            logger.debug("Parsed '%s' as %s", node.info(), node.parseinfo.rule)
            return node
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
        self._ast = ast

    def info(self):
        parseinfo = self.parseinfo
        buffer = parseinfo.buffer
        line_info = buffer.line_info(parseinfo.pos)
        lines = parseinfo.text_lines()
        start = parseinfo.pos - line_info.start
        if len(lines) == 1:
            end = parseinfo.endpos - line_info.start
            return lines[0][start:end].strip()
        else:
            return lines[0][start:].strip() + "..."

    def accept(self, visitor):
        method_name = "visit_%s" % self.parseinfo.rule
        if hasattr(visitor, method_name):
            method = getattr(visitor, method_name)
        elif hasattr(visitor, "visit_default"):
            method = visitor.visit_default
        else:
            raise NotImplementedError("visit", self)
        return method(self)

    def __repr__(self):
        return "<{rule} '{info}'>".format(
            rule=self.parseinfo.rule,
            info=self.info(),
        )