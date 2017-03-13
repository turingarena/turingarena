#include "driver.h"

int pong = 0;

int evaluate() {
  int solution = algorithm_start("solution");
  int result = call_ping(solution);
  process_kill(solution);

  if(pong) {
    return 1;
  } else {
    return 0;
  }
}

int on_pong(int process_id) {
  pong = 1;
}