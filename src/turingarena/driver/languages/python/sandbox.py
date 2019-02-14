import errno
import sys

try:
    import seccomplite
except ImportError:
    seccomplite = None
    print("WARNING: no code sandboxing! Install seccomplite")


def init_sandbox():
    filter = seccomplite.Filter(seccomplite.ERRNO(errno.EACCES))
    filter.add_rule(seccomplite.ALLOW, "read", seccomplite.Arg(0, seccomplite.EQ, 0))
    filter.add_rule(seccomplite.ALLOW, "write", seccomplite.Arg(0, seccomplite.EQ, 1))
    filter.add_rule(seccomplite.ALLOW, "write", seccomplite.Arg(0, seccomplite.EQ, 2))
    filter.add_rule(seccomplite.ALLOW, "exit")
    filter.add_rule(seccomplite.ALLOW, "exit_group")
    filter.add_rule(seccomplite.ALLOW, "rt_sigreturn")
    filter.add_rule(seccomplite.ALLOW, "mmap")
    filter.add_rule(seccomplite.ALLOW, "munmap")
    filter.add_rule(seccomplite.ALLOW, "mremap")
    filter.add_rule(seccomplite.ALLOW, "brk")
    filter.add_rule(seccomplite.ALLOW, "lseek")
    filter.add_rule(seccomplite.ALLOW, "ioctl")
    filter.load()


def main():
    source_path, skeleton_path = sys.argv[1:]

    with open(source_path) as source_file:
        source_string = source_file.read()
    with open(skeleton_path) as skeleton_file:
        skeleton_string = skeleton_file.read()

    if seccomplite is not None:
        init_sandbox()

    class Wrapper: pass

    skeleton = Wrapper()
    source = Wrapper()

    # run skeleton and source
    exec(source_string, source.__dict__)
    exec(skeleton_string, skeleton.__dict__)

    skeleton.main(source)


if __name__ == "__main__":
    main()
