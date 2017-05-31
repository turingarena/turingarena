#include <taskwizard/support_proto.h>

int main() {
    driver_init();

    void* process = algorithm_create_process("solution");

    process_start(process);

    int value;
    fscanf(process_upward_pipe(process), "%d", &value);
    printf("value: %d (expected: 1)\n", value);

    process_stop(process);
}
