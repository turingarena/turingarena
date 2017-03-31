"""
Generate the parser python code with Grako
and load it with Python builtin 'exec'
"""

import os

from grako.codegen.python import codegen
from grako.grammars import EBNFBuffer
from grako.parser import GrammarGenerator
import pkg_resources


grammar_filename = pkg_resources.resource_filename("taskwizard", os.path.join("grammar", "grammar.ebnf"))

grammar = open(grammar_filename).read()
model = GrammarGenerator(grammar_name="Task", buffer_class=EBNFBuffer).parse(grammar, filename=grammar_filename)
parser_code = codegen(model)

exec(parser_code)
