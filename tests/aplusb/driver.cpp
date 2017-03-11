#include "driver.h"

int sum(int A, int B);

int evaluate(int A, int B) {
  task_set_current(task_start(1));
  int result = sum(A, B);
  fprintf(stderr, "Result: %d\n", result);
}
