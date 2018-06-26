int play(int n, int guess(int n)) {
    int min = 1, max = n, mid;
    while (true) {
        mid = (min+max)/2;
        switch ( guess(mid) ) {
            case -1: // too low
                min = mid+1;
                break;
            case 1:  // too high
                max = mid-1;
                break;
            default:  // correct
                return mid;
        }
    }
    return 1; // dummy
}

