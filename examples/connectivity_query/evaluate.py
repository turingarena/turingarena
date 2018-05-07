import random

import networkx as nx

from turingarena import *

algorithm = submitted_algorithm()

parts = (
    [nx.complete_graph(10) for _ in range(3)] +
    [nx.cycle_graph(10) for _ in range(3)]
)

graph = nx.disjoint_union_all(parts)

N = len(graph.nodes())
assert list(graph.nodes()) == list(range(N))  # check nodes are zero-based

Q = 10
D = [graph.degree(u) for u in graph.nodes()]
adj = [list(graph.neighbors(u)) for u in graph.nodes()]

cases = []
fail = False

try:
    with algorithm.run() as p:
        p.call.init(N, Q, D, adj)

        memory_usage = p.sandbox.get_info().memory_usage

        for t in range(Q):
            u = v = None
            while u == v:
                u, v = random.randint(0, N - 1), random.randint(0, N - 1)

            connected = bool(p.call.is_there_a_path(u, v))
            if nx.has_path(graph, u, v) == connected:
                cases.append((t, True))
            else:
                cases.append((t, False))
            print(f"Nodes {u} {v} -> {connected}")
except AlgorithmError:
    fail = True

evaluation_result(goals={
    f"case {i}:": "ok" if ok else "wrong"
    for i, ok in cases
})
