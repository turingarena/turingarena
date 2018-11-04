import sys

import commonmark
import lxml.etree as etree

from io import StringIO


class TextParser:
    def __init__(self, filename):
        self.root = self._parse_file(filename)

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

    def _do_get_description(self):


    @property
    def descriptions(self):
        return self._do_get_gescriptions()


if __name__ == '__main__':
    print(TextParser(sys.argv[1]).root)