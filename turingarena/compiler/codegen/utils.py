def indent_all(lines):
    for line in lines:
        yield indent(line)


def indent(line):
    if line is None:
        return None
    else:
        return "    " + line

def write_to_file(lines, file):
    for line in lines:
        if line is None:
            print("", file=file)
        else:
            print(line, file=file)
