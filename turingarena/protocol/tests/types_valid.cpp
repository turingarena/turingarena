extern int i, *ia, **iaa;

int get_i() {
    return i;
}

int get_ia(int j) {
    return ia[j];
}

int get_iaa(int j, int k) {
    return iaa[j][k];
}
