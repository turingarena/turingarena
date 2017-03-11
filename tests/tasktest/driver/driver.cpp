#include "supervisor_proto.h"
#include <bits/stdc++.h>

int main() {
  fprintf(stderr, "DRIVER!\n");
  int evaluate = read_file_open("evaluate");
  
  fprintf(stderr, "read_file_open ok\n");
  FILE* evaluate_pipe = read_file_pipe(evaluate);
  fprintf(stderr, "read_file_pipe ok\n");
  
  fprintf(stderr, "reading from flie...\n");
  int x;
  fscanf(evaluate_pipe, "%d", &x);
  fprintf(stderr, "reading from file ok\n");
  
  fprintf(stderr, "Read from 'evaluate': %d\n", x);
}
