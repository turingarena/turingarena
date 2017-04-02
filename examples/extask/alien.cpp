#define MINN 0
#define MAXN 1000

#define MINM 0
#define MAXM 1000

#define MINAi -0xFFFFFFFF
#define MAXAi 0x7FFFFFFF

int N;
int M;
int X;
int Y;
int A[MAXN];
int B[MAXN][MAXM];

int examine(int x, int y);

int cnt = 0;

int find_centre(int N, int Xi, int Yi) {
    if (cnt) {
        return examine(55, 42);
    }

    cnt++;
    return 117;
}

int deep = 5;
int cnt1 = 0;

int query() {
    if (!deep)
        return 578;
    deep--;
    
    int val = examine(deep, 42);
    A[deep % N] += val;
    B[cnt1++%N][deep % M]++;

    deep++;
    return val;
}

int update() {
    return 7;
}

int fill(int C[]) {

}