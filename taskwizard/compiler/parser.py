"""
Generate the parser python code with Grako
and load it with Python builtin 'exec'
"""

import pkg_resources
import grako

grammar = open(pkg_resources.resource_filename("taskwizard.compiler", "grammar.ebnf")).read()
parser_code = grako.tool.gencode("Task", grammar)

exec(parser_code)
