#include "turingarena.h"

#include <cstdlib>
#include <iostream>
#include <unistd.h>
#include <time.h>

std::string cwd() {
    char buff[1024];
    getcwd(buff, sizeof buff);
    return std::string(buff);
}

int main() {
    srand(time(nullptr));
    std::string source{getenv("SUBMISSION_FILE_SOURCE")};
    std::string interface{cwd() + "/interface.txt"};

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