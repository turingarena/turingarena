#include "turingarena.h"

#include <iostream>
#include <time.h>

int main() {
    srand(time(nullptr));
    std::string source{turingarena::get_submission_parameter("source")};
    std::string interface{turingarena::get_cwd() + "/interface.txt"};

    std::cout << "Starting algo with source = " << source << " interface = " << interface << '\n';
    for (int i = 0; i < 10; i++) {
        turingarena::Algorithm algo{source, interface};

        int a = rand() % 10;
        int b = rand() % 10;

        int c = algo.call_function("sum", a, b);

        std::cout << "test case #" << i << ": " << a << " + " << b << " = " << c << "  ";
        if (c == a + b) {
            std::cout << "CORRECT\n";
        } else {
            std::cout << "WRONG\n";
        }
    }
}