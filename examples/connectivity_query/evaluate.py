import random

import networkx as nx


def evaluate(algorithm):
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

    with algorithm.run(global_variables=dict(N=N, Q=Q, D=D, adj=adj)) as p:

        memory_usage = p.sandbox.get_info().memory_usage
        print(f"Memory usage: {memory_usage} bytes")

        for _ in range(Q):
            u = v = None
            while u == v:
                u, v = random.randint(0, N - 1), random.randint(0, N - 1)

            connected = bool(p.call.is_there_a_path(u, v))
            if nx.has_path(graph, u, v) == connected:
                print("Correct")
            else:
                print("Wrong")
            print(f"Nodes {u} {v} -> {connected}")
