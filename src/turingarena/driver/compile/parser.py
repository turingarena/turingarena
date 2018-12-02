import logging
from functools import lru_cache

import tatsu

from turingarena.driver.compile.grammar import grammar_ebnf

logger = logging.getLogger(__name__)


@lru_cache(None)
def get_grammar():
    return tatsu.compile(grammar_ebnf)


def parse_interface(text):
    return get_grammar().parse(text, start="interface", asmodel=False, parseinfo=True)


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
