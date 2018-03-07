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

source_loaded = False


def load_source():
    """
    Executes the algorithm source.

    Called by the skeleton on demand, at the first function invocation.
    At that time, all the global variables are loaded
    and can be simply import'd by the algorithm source.
    """
    global source_loaded
    if source_loaded: return
    source_loaded = True
    exec(source_string, source.__dict__)


skeleton.__dict__["__load_source__"] = load_source

# execute the modules source file
exec(skeleton_string, skeleton.__dict__)

# execute skeleton main
skeleton.main()

# terminate sandbox 
exit(0)
