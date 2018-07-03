#include "turingarena.h"

#include <iostream>
#include <array>

int main() {
    std::array<int, 10> A{4, 5, 1, 2, 8, 9, 0, 3, 7, 6};
    turingarena::Algorithm algorithm{turingarena::get_submission_parameter("source")};
    std::cerr << "Algorithm started\n";
    algorithm.call_procedure("sort", A.size(), A);
    for (int i = 0; i < A.size(); i++) {
        int e = algorithm.call_function("get_element", i);
        if (i != e) {
            std::cout << "WRONG" << " " << i << " " << e << '\n';
            return 0;
        }
    }
    std::cout << "CORRECT\n";
}
