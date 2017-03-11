#include "driver.h"

int sum(int A, int B);

int evaluate(int A, int B) {
  int solution = algorithm_start("solution");
  set_active_algorithm(solution);
  int result = sum(A, B);
  algorithm_kill(solution);
  fprintf(stderr, "Result: %d\n", result);
  exit(0);
}
