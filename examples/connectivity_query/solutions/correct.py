
from skeleton import N, adj

def DFS(u, v, a):
    a[u] = True
    if u == v:
        return True
    for w in adj[u]:
        if not a[w] and DFS(w, v, a):
            return True
    return False

def is_there_a_path(u, v):
    a = [False for _ in range(N)]
    return 1 if DFS(u, v, a) else 0


