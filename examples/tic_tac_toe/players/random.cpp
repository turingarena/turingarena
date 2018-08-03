#include <cstdlib>
#include <ctime>

// Constant declarations
#define ROWS 3
#define COLS 3
#define EMPTY 0
#define PLAYER 1
#define OPPONENT 2

// initialize random number generator
__attribute__((constructor)) void init() {
    srand(time(nullptr));
}

// find a random empty cell and place here
void play_move(int **grid, void place_at(int y, int x)) {
    int x, y;
    do {
        y = rand() % ROWS;
        x = rand() % COLS;
    } while (grid[y][x] != EMPTY);

    place_at(y, x);
}
