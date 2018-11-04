import sys

import commonmark
import lxml.etree as etree

from io import StringIO


def parse_markdown(markdown_text):
    return commonmark.commonmark(markdown_text)


def parse_html(html_text):
    parser = etree.HTMLParser()
    string_io = StringIO(html_text)
    return etree.parse(string_io, parser)


def parse_file(filename):
    with open(filename) as f:
        markdown_text = f.read()
    html_text = parse_markdown(markdown_text)
    return parse_html(html_text)


if __name__ == '__main__':
    print(parse_file(sys.argv[1]))