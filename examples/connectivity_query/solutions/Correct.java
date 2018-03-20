class Solution extends Skeleton {
    // global int N;
    // global int Q;
    // global int[] D;
    // global int[][] adj;

    void preprocess() {
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
