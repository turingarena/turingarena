import errno
import os
import resource
import sys
from seccomplite import Filter, ERRNO, ALLOW, TRAP


def init_sandbox():
    filter = Filter(TRAP)
    # no need to specify arguments of read/write (there should not be any other readable/writable fd)
    for syscall in [
        "read", "write", "readv", "writev",  # base I/O
        "lseek", "ioctl", "fstat",
        "exit", "exit_group", "rt_sigreturn",
        "mmap", "munmap", "mremap", "brk",
        "execve",
        "arch_prctl", "uname", "set_tid_address",
        "time",
    ]:
        filter.add_rule(ALLOW, syscall)
    for syscall in [
        "access", "madvise", "readlink",
    ]:
        filter.add_rule(ERRNO(errno.EACCES), syscall)
    filter.load()


def main():
    a = [None] * 5000000
    del a

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    print(f"FROM SANDBOX BEFORE: {rusage.ru_maxrss}", file=sys.stderr)

    pid = os.getpid()

    cmd = f"echo 5 > /proc/{pid}/clear_refs"
    print(f"FROM SANDBOX: {cmd}", file=sys.stderr)
    os.system(cmd)

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    print(f"FROM SANDBOX AFTER:  {rusage.ru_maxrss}", file=sys.stderr)

    a = [None] * 10000000
    del a

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    print(f"FROM SANDBOX NOW:  {rusage.ru_maxrss}", file=sys.stderr)

    init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    os.execl(sys.argv[1], sys.argv[1])


if __name__ == "__main__":
    main()
