void cb1();
void cb2();

int test() {
    cb1();
    cb2();
    cb2();
    cb1();
    return 1;
}
