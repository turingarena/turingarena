from taskwizard.compiler.grammar import GrammarParser


def main():
    print(GrammarParser().parse(open("tests/test.task").read()))
