#include "driver.h"

int sum(int A, int B);

int evaluate(int A, int B) {
  set_active_algorithm(start_algorithm("player1"));
  int result = sum(A, B);
  fprintf(stderr, "Result: %d\n", result);
}
