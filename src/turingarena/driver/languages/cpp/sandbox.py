import errno
import os
import sys

try:
    import seccomplite
except ImportError:
    seccomplite = None
    print("WARNING: no code sandboxing! Install seccomplite")


def init_sandbox():
    filter = seccomplite.Filter(seccomplite.TRAP)
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
        filter.add_rule(seccomplite.ALLOW, syscall)
    for syscall in [
        "access", "madvise", "readlink",
    ]:
        filter.add_rule(seccomplite.ERRNO(errno.EACCES), syscall)
    filter.load()


def main():
    if seccomplite is not None:
        init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    os.execle(sys.argv[1], sys.argv[1], {})


if __name__ == "__main__":
    main()
