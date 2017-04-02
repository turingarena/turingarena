import unittest

from taskwizard.definition.semantics import Semantics

from taskwizard.language.cpp.codegen import CodeGenerator
from taskwizard.parser import TaskParser

parser = TaskParser(semantics=Semantics())

protocol_definition = """\
protocol p {
    input N, M;
    for(i : 1..N) {
        input A[i];
    }
}
"""

expected_code = """\
scanf("%d%d", &N, &M);
for(i=1; i<=N; i++) {
    scanf("%d", &A[i]);
}
"""

class TestProtocolCpp(unittest.TestCase):

    def test(self):
        protocol = parser.parse(protocol_definition, rule_name="protocol_declaration")

        code = '\n'.join(CodeGenerator().generate_protocol(protocol)) + '\n'
        self.assertEqual(expected_code, code)
