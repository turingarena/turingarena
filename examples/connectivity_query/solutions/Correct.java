class Solution extends Skeleton {
    int N;
    int[] D;
    int[][] adj;

    void init(int _N, int _Q, int *_D, int **_adj) {
        N = _N;
        D = _D;
        adj = _adj;
    }

    boolean DFS(int u, int v, boolean a[]) {
        a[u] = true;
        if (u == v) 
            return true;
        for (int w : adj[u]) {
            if (!a[w] && DFS(w, v, a)) 
                return true;
        }
        return false; 
    }

    int is_there_a_path(int u, int v) {
        return DFS(u, v, new boolean[N]) ? 1 : 0;
    }
}
