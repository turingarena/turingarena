import errno
import sys
import os

from seccomplite import Filter, Arg, ERRNO, ALLOW, EQ, TRAP


def init_sandbox():
    filter = Filter(TRAP)
    filter.add_rule(ALLOW, "read", Arg(0, EQ, 0))
    filter.add_rule(ALLOW, "write", Arg(0, EQ, 1))
    filter.add_rule(ALLOW, "write", Arg(0, EQ, 2))
    filter.add_rule(ALLOW, "exit")
    filter.add_rule(ALLOW, "exit_group")
    filter.add_rule(ALLOW, "rt_sigreturn")
    filter.add_rule(ALLOW, "mmap")
    filter.add_rule(ALLOW, "munmap")
    filter.add_rule(ALLOW, "mremap")
    filter.add_rule(ALLOW, "brk")
    filter.add_rule(ALLOW, "lseek")
    filter.add_rule(ALLOW, "ioctl")
    filter.add_rule(ALLOW, "execve")
    filter.add_rule(ALLOW, "arch_prctl")
    filter.add_rule(ALLOW, "uname")
    filter.add_rule(ALLOW, "fstat")
    filter.add_rule(ERRNO(errno.EACCES), "readlink")
    filter.load()


def main():
    init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    os.execl(sys.argv[1], sys.argv[1])


if __name__ == "__main__":
    main()
