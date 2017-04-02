#include "driver.h"

#include <cstdlib>

const int N_MAX = 1000;


int on_alien_examine(int x, int y) {

}

int on_alien_solution(int x, int y) {
    
}


int evaluate() {
  srand(get_seed());
  int A = rand() % N_MAX;
  int B = rand() % N_MAX;

  int solution = algorithm_create_process("solution");
  process_start(solution);
  int result = call_alien_sum(solution, A, B);
  process_stop(solution);

  if(result == A+B) {
    return 1;
  } else {
    return 0;
  }
}
