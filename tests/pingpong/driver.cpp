#include "driver.h"

int pong = 0;

int evaluate() {
  int solution = algorithm_create_process("solution");
  
  process_start(solution);
  int result = call_pingpong_ping(solution);
  process_stop(solution);

  if(pong) {
    return 1;
  } else {
    return 0;
  }
}

int on_pingpong_pong(int process_id) {
  pong = 1;
}

