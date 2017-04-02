{% import "macro.j2" as macro %}

#include <bits/stdc++.h>
#include "header.h"

#define support_trace(...) do { \
    fprintf(stderr, "ALGORITHM({{interface.name}}): "); \
    fprintf(stderr, __VA_ARGS__); \
} while(0)

{{ macro.generate_protocol(interface.callback_functions.values(), interface.functions.values()) }}

int main() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    accept_callbacks();
}
