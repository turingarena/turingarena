{% import "macro.cpp.j2" as macro %}

#include <bits/stdc++.h>
#include "driver.h"

int current_process_id;

#define support_trace(...) do { \
    fprintf(stderr, "DRIVER({{driver.name}}): communication with stdin/out: "); \
    fprintf(stderr, __VA_ARGS__); \
} while(0) 

#define support_trace_driver(process_id,...) do { \
    fprintf(stderr, "DRIVER({{driver.name}}): communication with process(%d): ", current_process_id); \
    fprintf(stderr, __VA_ARGS__); \
} while(0) 

{% for interface in task.interfaces.values() %}
    {{ macro.generate_protocol(
        interface.functions.values(),
        interface.callback_functions.values(),
        driver=True,
        interface_name=interface.name) }}
{% endfor %}

{{ macro.generate_protocol([], driver.functions.values()) }}

int main() {
    fprintf(stderr, "DRIVER({{driver.name}}): started.\n");
    driver_init();
    fprintf(stderr, "DRIVER({{driver.name}}): driver_init() successful.\n");
    accept_callbacks();
    fprintf(stderr, "DRIVER({{driver.name}}): about to exit.\n");
}
