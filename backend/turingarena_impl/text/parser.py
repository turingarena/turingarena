import sys
from io import StringIO

import commonmark
import lxml.etree as etree

from turingarena_impl.text.visitor import TextVisitor


class DescriptionVisitor(TextVisitor):
    def visit_description(self, el):
        yield el.attrib['for'], "".join(el.itertext())

    def generic_visit(self, el):
        for c in el:
            yield from self.visit(c)


class TextParser:
    def __init__(self, filename):
        self.root = self._parse_file(filename).getroot()

    @staticmethod
    def _parse_markdown(markdown_text):
        return commonmark.commonmark(markdown_text)

    @staticmethod
    def _parse_html(html_text):
        parser = etree.HTMLParser()
        string_io = StringIO(html_text)
        return etree.parse(string_io, parser)

    def _parse_file(self, filename):
        with open(filename) as f:
            markdown_text = f.read()
        html_text = self._parse_markdown(markdown_text)
        return self._parse_html(html_text)

    @property
    def descriptions(self):
        return dict(DescriptionVisitor().visit(self.root))


if __name__ == '__main__':
    parser = TextParser(sys.argv[1])
    print(dir(parser.root))

    print(parser.descriptions)
