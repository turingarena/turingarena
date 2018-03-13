import random
import networkx as nx

N = 100  # number of nodes
Q = 100   # number of queries


def evaluate(algorithm):
    # create random graph
    g = nx.fast_gnp_random_graph(N, 0.1)

    # set random edge weight
    for u, v, d in g.edges(data=True):
        d['weight'] = random.randint(1, 1000)

    print("running algorithm")
    with algorithm.run(global_variables=dict(N=N, E=len(g.edges()), Q=Q)) as p:

        print("adding edges")
        for u, v, d in g.edges(data=True):
            p.call.add_edge(u, v, d['weight'])

        memory_usage = p.sandbox.get_info().memory_usage
        print(f"Memory usage: {memory_usage} bytes")

        for _ in range(Q):
            u = v = None
            while u == v:
                u, v = random.randint(1, N-1), random.randint(1, N-1)

            try:
                r = nx.dijkstra_path_length(g, u, v)
            except nx.NetworkXNoPath:
                r = -1

            res = p.call.shortest_path(u, v)

            if res != r:
                print(f"Wrong! {res} != {r}")
            else:
                print("ok")

