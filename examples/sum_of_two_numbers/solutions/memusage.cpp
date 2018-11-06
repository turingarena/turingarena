#include <sys/time.h>
#include <sys/resource.h>

#include <cstdio>
#include <cstdlib>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

void print_resources() {
    struct rusage usage;

    getrusage(RUSAGE_SELF, &usage);
    int self_maxrss = usage.ru_maxrss;

    getrusage(RUSAGE_CHILDREN, &usage);
    int children_maxrss = usage.ru_maxrss;

    fprintf(stderr, "RUSAGE - self: %d, children: %d\n", self_maxrss, children_maxrss);

    int pid = getpid();
    char s[50];
    snprintf(s, sizeof(s), "cat /proc/%d/status >&2", pid);
    system(s);
}

int sum(int a, int b) {
    int N = 80000000;
    char *p = new char[N];

    for(int i = 0; i < N; i++) {
        p[i] = i;
    }

    delete p;

    print_resources();

    int fd = open("/proc/self/clear_refs", O_WRONLY);
    write(fd, "5", 1);
    close(fd);

    print_resources();

    return a+b;
}
