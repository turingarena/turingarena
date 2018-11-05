import networkx as nx

from turingarena import *

N = 100  # number of nodes
Q = 100  # number of queries

# create random graph
g = nx.fast_gnp_random_graph(N, 0.1)

cases = []

# set random edge weight
for u, v, d in g.edges(data=True):
    d['weight'] = random.randint(1, 1000)

print("running algorithm")

try:
    all_correct = True
    with run_algorithm(submission.source) as p:
        D = [g.degree(u) for u in g]
        A = [g.neighbors(u) for u in g]
        W = [[w for _, _, w in g.edges(u, data="weight")] for u in g]

        p.procedures.init(N, Q, D, A, W)

        for k in range(Q):
            u = v = None
            while u == v:
                u, v = random.randint(0, N - 1), random.randint(0, N - 1)

            try:
                r = nx.dijkstra_path_length(g, u, v)
            except nx.NetworkXNoPath:
                r = -1

            res = p.functions.shortest_path(u, v)
            if res != r:
                print(f"Wrong! {res} != {r}")
            else:
                print("ok")
            all_correct &= res == r
except AlgorithmError:
    all_correct = False

evaluation.data(dict(goals={
    "correct": all_correct,
}))
