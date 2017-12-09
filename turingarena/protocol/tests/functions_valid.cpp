void args(int a, int b) {
}

void no_args() {
}

void no_return_value(int a) {
}

int return_value(int a) {
    return 0;
}

void cb_no_args();
void cb_args(int a, int b);
void cb_no_return_value(int a);
int cb_return_value(int a);

int invoke_callbacks() {
    cb_no_args();
    cb_args(2, 3);
    cb_no_return_value(4);
    return cb_return_value(5);
}
