#include "driver.h"

int evaluate(int A, int B) {
  int solution = algorithm_start("solution");
  int result = call_sum(solution, A, B);
  algorithm_kill(solution);

  if(result == A+B) {
    return 1;
  } else {
    return 0;
  }
}
