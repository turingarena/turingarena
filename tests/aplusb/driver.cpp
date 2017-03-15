#include "driver.h"

#include <cstdlib>

const int N_MAX = 1000;

int evaluate() {
  int solution = algorithm_start("solution");

  srand(get_seed());
  int A = rand() % N_MAX;
  int B = rand() % N_MAX;

  int result = call_aplusb_sum(solution, A, B);
  process_kill(solution);

  if(result == A+B) {
    return 1;
  } else {
    return 0;
  }
}
