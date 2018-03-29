int **position_mapping;

void player_move(int pos);

int pc_move();

// 0 = EMPTY, 1=PLAYER, 2=ENEMY
int match[3][3] = { {0,0,0}, {0,0,0}, {0,0,0} };

void start_new_game() {
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            match[i][j] = 0;
}

int play_first_round() {
    // take the center
    match[1][1] = 1;
    return position_mapping[1][1];
}

int play_a_round( int enemy_y, int enemy_x) {

    match[enemy_y][enemy_x] = 2;

    // TODO calculate perfect move
    // find if can win
    // try to stop enemy victory
    // don't open to enemy attack
    int my_y, my_x;

    return position_mapping[my_y][my_x];
}

