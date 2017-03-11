#include "driver.h"

int sum(int A, int B);

int evaluate(int A, int B) {
  algorithm_start("player1");
  int result = sum(A, B);
  fprintf(stderr, "Result: %d\n", result);
}
