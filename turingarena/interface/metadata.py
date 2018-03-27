import re
from xml.etree import ElementTree
from xml.sax.saxutils import quoteattr

import CommonMark

reInlineMath = re.compile(r"\$([^\$]+)\$", flags=re.MULTILINE)
reDisplayMath = re.compile(r"^\$\$([^\$]+)\$\$", flags=re.MULTILINE)


def xml_to_dict(element):
    return dict(
        element_type=element.tag,
        attributes=dict(element.items()),
        children=list(xml_children(element)),
    )


def xml_children(element):
    if element.text is not None:
        yield element.text
    for child in element:
        yield xml_to_dict(child)
        if element.tail is not None:
            yield element.tail


def parse_markdown(text):
    if not text: return None

    text = reDisplayMath.sub(lambda m: f'<math src={quoteattr(m.group(1))} />', text)
    text = reInlineMath.sub(lambda m: f'<math src={quoteattr(m.group(1))} />', text)
    print(text)
    html = CommonMark.commonmark(text)
    print(html)
    ast = ElementTree.fromstring(f"<turingarena>{html}</turingarena>")
    return list(xml_children(ast))
