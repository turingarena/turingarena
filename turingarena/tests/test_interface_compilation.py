import pkg_resources
import pytest

from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.model.model import InterfaceDefinition


def interface_testcases(lines):
    k = None
    title = None
    marker = "=== "
    for i, line in enumerate(lines + [marker]):
        if line.startswith(marker):
            if k is not None:
                yield title, lines[k + 1:i]
            k = i
            title = line[len(marker):].strip()


with open(pkg_resources.resource_filename(__name__, "interface_tests.txt")) as f:
    lines = f.readlines()


def process_line(line):
    message_marker = "  !!!"

    if line.find(message_marker) == -1:
        return line, None

    line, start_pos = extract_marker(line, "___ ")
    line, end_pos = extract_marker(line, " ___")
    line, message = extract_message(line, message_marker)

    return line, (start_pos, end_pos, message)


def extract_message(line, message_marker):
    message_pos = line.index(message_marker)
    message = line[message_pos + len(message_marker):].strip()
    line = line[:message_pos]
    return line, message


def extract_marker(line, marker):
    startpos = line.index(marker)
    line = line[:startpos] + line[startpos + len(marker):]
    return line, startpos


cases = list(interface_testcases(lines))
ids = [t for (t, source_lines) in cases]


@pytest.mark.parametrize(
    "title, source_lines",
    cases,
    ids=ids,
)
def test_compile_interface(title, source_lines):
    processed_lines = [
        process_line(l) for l in source_lines
    ]

    interface_text = "\n".join(line for line, _ in processed_lines)
    infos = [
        (lineno, info)
        for lineno, (line, info) in enumerate(processed_lines)
        if info is not None
    ]

    # assume there is a single error for now
    [(lineno, (start_pos, end_pos, message))] = infos

    with pytest.raises(ProtocolError) as excinfo:
        InterfaceDefinition.compile(interface_text)

    start_info, end_info = excinfo.value.line_info()
    assert excinfo.value.message == message
    assert start_info.col == start_pos
