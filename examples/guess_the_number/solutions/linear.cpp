int guess(int n);

int play(int n) {
    int val = 1;
    while ( val <= n && guess(val++) != 0 ) ;
    return val-1;
}
