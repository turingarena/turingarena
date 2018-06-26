import random

import networkx as nx

from turingarena import *

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
    with run_algorithm(submission.source) as p:
        p.procedures.init(N, Q, D, adj)

        #memory_usage = p.sandbox.get_info().memory_usage

        for t in range(Q):
            u = v = None
            while u == v:
                u, v = random.randint(0, N - 1), random.randint(0, N - 1)

            connected = bool(p.functions.is_there_a_path(u, v))

            evaluation.data(dict(goals={
                f"case {t}:": nx.has_path(graph, u, v) == connected
            }))
            print(f"Nodes {u} {v} -> {connected}")
except AlgorithmError:
    fail = True
