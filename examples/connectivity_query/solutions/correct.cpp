// number of nodes
int N;

// number of queries
int Q;

// edge degree
int *D;

// adjacent list
int **adj;

bool DFS(int u, int v, bool a[]) {
    a[u] = true;
    if (u == v)
        return true;
    for (int i = 0; i < D[u]; i++) {
        int w = adj[u][i];
        if (!a[w] && DFS(w, v, a))
            return true;
        }
    return false;
}

int is_there_a_path(int u, int v) {
    bool a[N];
    return DFS(u, v, a) ? 1 : 0;
}


