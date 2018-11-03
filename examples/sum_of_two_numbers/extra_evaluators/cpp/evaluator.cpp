#include "turingarena.h"

#include <iostream>
#include <time.h>

int main() {
    bool all_passed = true;
    
    srand(time(nullptr));
    std::string source{turingarena::get_submission_parameter("source")};

    std::cout << "Starting algo with source = " << source << '\n';
    for (int i = 0; i < 10; i++) {
        turingarena::Algorithm algo{source};

        int a = rand() % 10;
        int b = rand() % 10;

        int c = algo.call_function("sum", a, b);

        std::cout << "test case #" << i << ": " << a << " + " << b << " = " << c << "  ";
        if (c == a + b) {
            std::cout << "CORRECT\n";
        } else {
            std::cout << "WRONG\n";
            all_passed = false;
        }
    }

    if (all_passed)
        turingarena::evaluation_data("{\"goals\": {\"correct\": true}}");
    else
        turingarena::evaluation_data("{\"goals\": {\"correct\": false}}");
}