int sum(int a, int b) {
    int c = 0;
    for(int i = 0; i < 10000000; i++) {
        c += i;
        if(c % 2) {
            c += 1;
        }
    }
    if(c%2) {
        a ^= b;
        b ^= a;
        a ^= b;
    }
    return a+b;
}
