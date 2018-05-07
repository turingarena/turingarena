class Solution extends Skeleton {

    private int max(int a, int b) {
        return a > b ? a : b;
    }

    int find_best_sum(int N, int[][] V) {
        int [][] dyn = new int[N+1][N+1];
        for(int i = 0; i < N+1; i++)
            dyn[N][i] = 0;
        for(int i = N-1; i >= 0; i--)
            for(int j = 0; j < i; j++)
                dyn[i][j] = V[i][j] + max(dyn[i+1][j], dyn[i+1][j+1]);
        return dyn[1][0];
    }
}