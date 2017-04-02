#include <stdio.h>
#include <cassert>

/////////////////////////// LIMITS ///////////////////////////
#define MINN 0
#define MAXN 1000

#define MINM 0
#define MAXM 1000

#define MINAi -0xFFFFFFFF
#define MAXAi 0x7FFFFFFF
/////////////////////////// END LIMITS ///////////////////////////

extern int N;
extern int M;
extern int X;
extern int Y;
extern int A[MAXN];
extern int B[MAXN][MAXM];

extern int find_centre(int N, int Xi, int Yi);
extern int query();
extern int update();
extern int fill(int C[]);


int main() {
    scanf("%d%d", &N, &M);
    
    int find_centre_N;
    int find_centre_Xi;
    int find_centre_Yi;
    scanf("%d%d%d",
            &find_centre_N,
            &find_centre_Xi,
            &find_centre_Yi);

    int result = find_centre(find_centre_N, 
                            find_centre_Xi, 
                            find_centre_Yi);
    printf("ret %d\n", result);
    fflush(stdout);

    for (int i = 0; i < N; i++) {
        scanf("%d", &A[i]);
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            scanf("%d", &B[i][j]);
        }
    }

    scanf("%d%d%d",
            &find_centre_N,
            &find_centre_Xi,
            &find_centre_Yi);
    result = find_centre(find_centre_N, 
                            find_centre_Xi, 
                            find_centre_Yi);
    printf("ret %d\n", result);
    fflush(stdout);



    char c;
    scanf(" %c", &c);
    switch (c) {
        case 'u':
            result = update();
            printf("ret %d", result);
        break;

        case 'q':
            result = query();
            printf("ret %d", result);
        break;

        case 'f':
            int C[MAXN];
            result = fill(C);
            assert(result < MAXN);
            printf("ret %d\n", result);            
            for (int i = 0; i < result; i++) {
                printf("%d ", C[i]);
            }
            break;

    }
    puts("");

    for (int i = 0; i < N; i++) {
        printf("%d ", A[i]);
    }
    puts("");

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            printf("%d ", B[i][j]);
        }
        puts("");
    }
    fflush(stdout);
}

int examine(int x, int y) {
    int result;
    printf("examine %d %d\n", x, y);
    fflush(stdout);
    for (;;) {
        char c;
        fflush(stdout);
        scanf(" %c", &c);
        switch(c) {
            case 'q':
                result = query();
                printf("ret %d\n", result);
            break;
            case '#':
                goto exit_cycle;        
        }

        fflush(stdout);
        scanf(" %c", &c);
        switch(c) {
            case 'u':
                result = update();
                printf("%d\n", result);
            break;
        }
    }
exit_cycle:
    scanf("%d%d", &X, &Y);
    result = update();
    printf("%d\n", result);

    result;
    fflush(stdout);
    scanf("%d", &result);
    return result;
}