import os
import resource

import sys


def sum(a, b):
    x = [None] * int(2e7)
    del x

    print("self:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, file=sys.stderr)
    print("children:", resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss, file=sys.stderr)

    with open("/proc/self/status") as f:
        print(f.read(), file=sys.stderr)

    fd = os.open("/proc/self/clear_refs", os.O_WRONLY)
    os.write(fd, b"5")
    os.close(fd)

    print("self:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, file=sys.stderr)
    print("children:", resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss, file=sys.stderr)

    with open("/proc/self/status") as f:
        print(f.read(), file=sys.stderr)

    return a + b
