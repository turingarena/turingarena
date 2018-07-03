#include "turingarena.h"

#include <iostream>
#include <vector>
#include <array>
#include <cstdlib>
#include <ctime>
#include <algorithm>

int find_best_sum(const std::array<std::vector<int>, 100>& V) {
    int dyn[V.size() + 1][V.size() + 1];
    for(int i = 0; i < V.size() + 1; i++)
        dyn[V.size()][i] = 0;
    for(int i = V.size() - 1; i >= 0; i--)
        for(int j = 0; j < i; j++)
            dyn[i][j] = V[i][j] + std::max(dyn[i+1][j], dyn[i+1][j+1]);
    return dyn[1][0];
}

int main()
{
    srand(time(nullptr));

    std::array<std::vector<int>, 100> A;

    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < i; j++) {
            A[i].push_back(rand() % 100);
        }
    }
    
    int solution = find_best_sum(A);
    int result;

    {
        turingarena::Algorithm algorithm{turingarena::get_submission_parameter("source")};
        result = algorithm.call_function("find_best_sum", A.size(), A);
    }

    if (result == solution)
        std::cout << "CORRECT\n";
    else 
        std::cout << "WRONG\n";
}