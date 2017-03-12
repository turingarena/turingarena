#include "driver.h"

int evaluate(int A, int B) {
  int solution = algorithm_start("solution");

  int result = call_sum(solution, A, B);
  algorithm_kill(solution);

  fprintf(stderr, "Result: %d\n", result);
  return 0;
}
