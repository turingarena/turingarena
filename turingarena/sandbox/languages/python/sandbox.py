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


# read source and skeleton files to string
with open("source.py", "r") as source_file:
    source_string = source_file.read()

with open("skeleton.py", "r") as skeleton_file:
    skeleton_string = skeleton_file.read()

# enter sandbox enviroment. From here every system call that is not allowed will result in an Exception 
init_sandbox()

# create source and skeleton modules 
sys.modules["source"] = types.ModuleType("source")
sys.modules["skeleton"] = types.ModuleType("skeleton")

# import modules (because they are in sys.modules it will not try to access the filesystem)
import source
import skeleton


def load_source():
    exec(source_string, source.__dict__)


def my_import(name, *args, **kwargs):
    if name == "source":
        load_source()
    return __import__(name, *args, **kwargs)


import builtins

skeleton.__builtins__ = dict(
    builtins.__dict__,
    __import__=my_import,
)

# execute the modules source file
exec(skeleton_string, skeleton.__dict__)

# execute skeleton main
skeleton.main()

# terminate sandbox 
exit(0)
