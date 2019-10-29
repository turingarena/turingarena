#include <cstdio>
#include <cstdlib>
#include <cassert>

#define MAX 1000000

int main(int argc, char** argv){
    assert(argc == 4);
    int N = atoi(argv[1]);  // N
    int T = atoi(argv[2]);  // Tipo (1=esempio,2=dispari,3=pari,4=misti)
    int S = atoi(argv[3]);  // Seed

    if (T == 1) {  // Caso di prova
        if (S == 1) printf("10\n1 2 3 4 5 6 7 8 9 10\n");
        else printf("2\n13 13\n");
        return 0;
    }
    srand(S);

    printf("%d\n", N);
    for (int i=0; i<N; i++) {
        int x;
        if (T == 2) {                // Tutti dispari
            x = rand() % (MAX / 2);
            x = x * 2 + 1;
        } else if (T == 3) {         // Tutti pari
            x = rand() % (MAX / 2);
            x = x * 2;
        } else {                     // Misti
            x = rand() % MAX;
        }
        printf("%d%c", x, "\n "[i+1<N]);
    }
}

