import errno
import os
import sys
from seccomplite import Filter, ERRNO, ALLOW, TRAP


def init_sandbox():
    filter = Filter(TRAP)
    # no need to specify arguments of read/write (there should not be any other readable/writable fd)
    for syscall in [
        "read", "write", "readv", "writev",  # base I/O
        "lseek", "ioctl", "fstat",  # used by
        "exit", "exit_group", "rt_sigreturn",
        "mmap", "munmap", "mremap", "brk",
        "execve", "arch_prctl",
        "uname", "set_tid_address",
    ]:
        filter.add_rule(ALLOW, syscall)
    filter.add_rule(ERRNO(errno.EACCES), "madvise")
    filter.add_rule(ERRNO(errno.EACCES), "readlink")
    filter.load()


def main():
    init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    os.execl(sys.argv[1], sys.argv[1])


if __name__ == "__main__":
    main()
