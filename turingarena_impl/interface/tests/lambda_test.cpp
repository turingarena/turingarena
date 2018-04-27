/*
    This file is a proof of concept for using C++ lambdas for callbacks.
    The idea is to use 'static' variables in main,
    so that lambdas do not need to capture them and can be converted to function pointers.
    This way, we have all the advantages of lambdas (local definition and scoping)
    without needing C++ templates in generated code, just C function pointers.
*/

#include <cstdio>

int f(int x, void callback(int b)) {
    callback(x);
}

int main() {
    // int a; --> 'a' not captured
    static int a;
    { static int c; } // local definition

    static void (*mycallback)(int) = [](int b) {
        // a = c  --> 'c' not declared
        printf("a: %d, b: %d\n", a, b);
    };

    a = 3;
    f(5, mycallback);
}
