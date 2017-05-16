from unittest.case import TestCase

from taskwizard.definition.grammar import grammar


text = r"""

interface i {
    const int N_MAX = 1000;

    global int N, M;
    global int[] U, V;
    global int[][] A;

    function int preprocess(int a, int b);
    function int solve(int a, int b);

    callback int choose(int a, int b) {
        output a, b;
        input r;
        return r;
    }

    main {
        input N, M;
        alloc (U, V) = int[1..M];
        alloc A = int[1..N][1,,N];
        for(i : 1..M) {
            input U[i], V[i];
        }
        do {
            local enum {U, R} C;
            input C;
            switch(C) {
                case(U) {
                    continue;
                }
                case(R) {
                    break;
                }
            }
        }
        local int u, v;
        input u, v;
        call preprocess(u, v);
        call solve2(u, v) -> a;
        output S;
    }
}
"""


class TestParser(TestCase):

    def test_parse(self):
        grammar.parse(text, "interface_definition", parseinfo=True)
