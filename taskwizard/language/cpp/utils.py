def indent_all(lines):
    for line in lines:
        if line is None:
            yield None
        else:
            yield "    " + line


def write_to_file(lines, file):
    for line in lines:
        if line is None:
            print("", file=file)
        else:
            print(line, file=file)
