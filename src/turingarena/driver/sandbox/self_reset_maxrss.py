import os
import resource

import time


def main():
    pid = os.getpid()

    a = [None] * int(1e7)
    del a

    print("BEFORE:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    with open("/proc/self/status") as f:
        print(f.read())

    fd = os.open("/proc/self/clear_refs", os.O_WRONLY)
    os.write(fd, b"5")
    os.close(fd)

    x = [None] * int(1e4)

    print("AFTER:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    with open("/proc/self/status") as f:
        print(f.read())


if __name__ == '__main__':
    main()
