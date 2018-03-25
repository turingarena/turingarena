import logging

import tatsu

from turingarena.interface.grammar import grammar_ebnf

logger = logging.getLogger(__name__)

grammar = tatsu.compile(grammar_ebnf)


def parse_interface(text, **kwargs):
    return grammar.parse(text, **kwargs, asmodel=False, parseinfo=True)


def get_line(parseinfo):
    buffer = parseinfo.buffer
    line_info = buffer.line_info(parseinfo.pos)
    lines = parseinfo.text_lines()
    start = parseinfo.pos - line_info.start
    if len(lines) == 1:
        end = parseinfo.endpos - line_info.start
        return lines[0][start:end].strip()
    else:
        return lines[0][start:].strip() + "..."
