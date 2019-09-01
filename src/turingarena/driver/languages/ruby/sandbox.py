import errno
import os
import sys

import seccomplite


def init_sandbox():
    filter = seccomplite.Filter(seccomplite.TRAP)

    for syscall in [
        'openat', 'lstat', 'read', 'close',
        'stat', 'fstat', 'ioctl', 'brk', 'mmap',
        'mprotect', 'lseek', 'rt_sigaction',
        'munmap', 'getdents', 'access', 'getrandom',
        'getpid', 'rt_sigprocmask', 'pipe2', 'prlimit64',
        'sigaltstack', 'getcwd', 'sched_getaffinity',
        'clock_gettime', 'execve', 'arch_prctl',
        'set_robust_list', 'set_tid_address', 'write',
        'readv', 'exit', 'exit_group', 'rt_sigreturn',
        'mremap', 'uname', 'time'
    ]:
        filter.add_rule(seccomplite.ALLOW, syscall)

    for syscall in [
        "madvise", "readlink",
    ]:
         filter.add_rule(seccomplite.ERRNO(errno.EACCES), syscall)
    filter.load()


def main():
    init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    os.execle(sys.argv[1], sys.argv[1], {})


if __name__ == "__main__":
    main()
