import grako
from grako.ast import AST


class Semantics:

    def __init__(self, cls):
        self.deps = cls.get_all_deps();
        self.rule_map = {
            cls2.get_grammar_rule(): cls2
            for cls2 in self.deps
            if issubclass(cls2, AbstractSyntaxNode)
            if cls2.get_grammar_rule() is not None
        }

    def _default(self, ast, *args, **kwargs):
        if isinstance(ast, AST):
            rule = ast.parseinfo.rule
            assert rule in self.rule_map
            return self.rule_map[rule](ast, *args, **kwargs)

        return ast


class AbstractSyntaxFragment:

    @classmethod
    def get_grammar_fragment(cls):
        return cls.__dict__.get("grammar", "")

    @classmethod
    def get_direct_deps(cls):
        return cls.__dict__.get("grammar_deps", lambda: [])()

    @classmethod
    def get_all_deps(cls):
        stack = [cls]
        deps = []
        deps_set = set()
        while stack:
            cls2 = stack.pop()
            assert issubclass(cls2, AbstractSyntaxFragment)
            if not cls2 in deps_set:
                deps_set.add(cls2)
                deps.append(cls2)
                stack.extend(reversed(cls2.get_direct_deps()))
        deps.reverse() # post-order
        return deps

    @classmethod
    def get_grammar(cls):
        return r"""
            @@comments :: /\/\*(.|\n|\r)*\*\//
            @@eol_comments :: /\/\/.*$/
        """ + "\n".join(cls2.get_grammar_fragment() for cls2 in cls.get_all_deps())


class AbstractSyntaxNode(AbstractSyntaxFragment):

    def __init__(self, ast):
        for attr, value in ast.items():
            setattr(self, attr, value)

    @classmethod
    def get_explicit_grammar_rule(cls):
        return cls.__dict__.get("grammar_rule", None)

    @classmethod
    def get_grammar_rule(cls):
        rule = cls.get_explicit_grammar_rule()
        if rule is None:
            rule = cls.get_grammar_fragment().lstrip().split(maxsplit=2)[0]
        return rule

    @classmethod
    def parse(cls, text):
        rule_name = cls.get_grammar_rule()
        assert rule_name is not None
        grammar = cls.get_grammar()
        grammar_model = grako.compile(grammar)
        return grammar_model.parse(text, rule_name, parseinfo=True, semantics=Semantics(cls))
