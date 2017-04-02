import unittest

from taskwizard.definition.semantics import Semantics

from taskwizard.language.cpp.codegen import CodeGenerator
from taskwizard.parser import TaskParser

parser = TaskParser(semantics=Semantics())


class TestProtocolCpp(unittest.TestCase):

    def test(self):
        interface_definition = """
            interface a {
                protocol p {
                    input N, M;
                }
            }
        """

        expected_code = 'scanf("%d%d", &N, &M);'

        interface = parser.parse(interface_definition, rule_name="interface_definition")

        protocol = interface.protocols["p"]

        code = '\n'.join(CodeGenerator().generate_protocol(protocol))
        self.assertEqual(code, expected_code)
