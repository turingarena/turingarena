#include "supervisor_proto.h"
#include <bits/stdc++.h>

int main() {
  fprintf(stderr, "DRIVER!\n");
  int evaluate = read_file_open("evaluate");
  
  fprintf(stderr, "DRIVER: read_file_open ok\n");
  FILE* evaluate_pipe = read_file_pipe(evaluate);
  fprintf(stderr, "DRIVER: read_file_pipe ok\n");
  
  fprintf(stderr, "DRIVER: reading from flie...\n");
  int x;
  fscanf(evaluate_pipe, "%d", &x);
  fprintf(stderr, "DRIVER: reading from file ok\n");
  
  fprintf(stderr, "DRIVER: Read from 'evaluate': %d\n", x);
}
