#include "turingarena.h"

#include <cstdlib>
#include <iostream>
#include <unistd.h>
#include <time.h>

int main() {
    srand(time(nullptr));

    for (int i = 0; i < 10; i++) {
        turingarena::Algorithm algo{getenv("TURINGARENA_SUBMISSION_SOURCE"), std::string(getcwd(nullptr)) + "/interface.txt"};

        int a = rand() % 10;
        int b = rand() % 10;

        int c = algo.call_function("sum", a, b);

        std::cout "test case #" << i << ": " << a << " + " << b << " = " << c << "  "
        if (c == a + b) {
            std::cout << "CORRECT\n";
        } else {
            std::cout << "WRONG\n";
        }
    }
}