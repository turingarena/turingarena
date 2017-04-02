import unittest

from taskwizard.definition.semantics import Semantics

from taskwizard.language.cpp.codegen import CodeGenerator
from taskwizard.parser import TaskParser

parser = TaskParser(semantics=Semantics())


interface_definition = r"""
interface a {
    int N;
    int M;
    int A[1..1000];
    int S;

    int solve(int N, int M);

    protocol p {
        input N, M;
        for(i : 1..N) {
            input A[i];
        }
        call S = solve(N, M);
        output S;
    }
}
"""

expected_interface_code = r"""
int N;
int M;
int A[1+1000];
int S;

void accept_p() {
    scanf("%d%d", &N, &M);
    for(i=1; i<=N; i++) {
        scanf("%d", &A[i]);
    }
    S = solve(N, M);
    printf("%d\n", S);
}
"""

expected_driver_code = r"""
int N;
int M;
int A[1+1000];
int S;

void send_a_p(int process_id) {
    FILE* dpipe = get_downward_pipe(process_id);
    FILE* upipe = get_upward_pipe(process_id);

    fprintf(dpipe, "%d %d\n", N, M);
    for(i=1; i<=N; i++) {
        fprintf(dpipe, "%d\n", A[i]);
    }
    fscanf(upipe, "%d", &S);
}
"""


class TestCodeGeneratorCpp(unittest.TestCase):

    def test_interface_support(self):
        interface = parser.parse(interface_definition, rule_name="interface_definition")

        code = '\n' + '\n'.join(CodeGenerator().generate_interface_support(interface)) + '\n'
        print(code)
        self.assertEqual(expected_interface_code, code)

    def test_driver_support(self):
        interface = parser.parse(interface_definition, rule_name="interface_definition")

        code = '\n' + '\n'.join(CodeGenerator().generate_interface_driver_support(interface)) + '\n'
        print(code)
        self.assertEqual(expected_driver_code, code)
