import errno
import sys
import types

from seccomplite import Filter, Arg, ERRNO, ALLOW, EQ


def init_sandbox():
    filter = Filter(ERRNO(errno.EACCES))
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
    filter.load()


def main():
    source_path, skeleton_path = sys.argv[1:]

    with open(source_path) as source_file:
        source_string = source_file.read()
    with open(skeleton_path) as skeleton_file:
        skeleton_string = skeleton_file.read()

    print(skeleton_string, file=sys.stderr)

    init_sandbox()

    # create skeleton module
    skeleton = sys.modules["skeleton"] = types.ModuleType("skeleton")
    source = sys.modules["_source"] = types.ModuleType("_source")

    # run skeleton and source
    exec(source_string, source.__dict__)
    exec(skeleton_string, skeleton.__dict__)

    skeleton.main()


if __name__ == "__main__":
    main()
