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
    with open("source.py", "r") as source_file:
        source_string = source_file.read()
    with open("skeleton.py", "r") as skeleton_file:
        skeleton_string = skeleton_file.read()

    init_sandbox()

    # From here every system call that is not allowed will result in an Exception

    run_skeleton(skeleton_string, source_string)


def run_skeleton(skeleton_string, source_string):
    # hook on 'import source'
    def my_import(name, *args, **kwargs):
        if name == "source":
            source = types.ModuleType("source")
            exec(source_string, source.__dict__)
            return source
        return __import__(name, *args, **kwargs)

    # create skeleton module
    skeleton = sys.modules["skeleton"] = types.ModuleType("skeleton")
    # patch skeleton builtins to add import hook
    import builtins
    skeleton.__builtins__ = dict(
        builtins.__dict__,
        __import__=my_import,
    )
    # run skeleton
    exec(skeleton_string, skeleton.__dict__)
    skeleton.main()


if __name__ == "__main__":
    main()
