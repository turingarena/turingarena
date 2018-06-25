#include <cstdlib>

void start(int n_moves) {
    srand(100);
}

int play(int i) {
    return rand()%3;
}

void done(int i, int my_move, int their_move) {}
