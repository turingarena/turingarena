import re
import textwrap
from collections import namedtuple

from turingarena.text.visitor import xmlvisitormethod

whitespace = re.compile(r'\s+')

Paragraph = namedtuple("Paragraph", ["words"])


class TextGenerator:
    def lines(self, el):
        return textwrap.wrap(" ".join(self.words(el)))

    @xmlvisitormethod
    def words(self, el):
        pass

    def words_node(self, el):
        if el.text is not None:
            yield from el.text.split()
        for c in el:
            yield from self.words(c)
        if el.tail is not None:
            yield from el.tail.split()
