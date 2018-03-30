import logging
import os
from distutils.sysconfig import get_python_lib

from turingarena.cli import docopt_cli

PTH_HEADER = "# TURINGARENA PROBLEM SET"

logger = logging.getLogger(__name__)


def get_pth_filename():
    # should be: prefix, *_ = site.getsitepackages()
    # but it fails due to: https://github.com/pypa/virtualenv/issues/355
    packages_dir = get_python_lib()
    pth_filename = os.path.join(packages_dir, "turingarena.pth")
    return pth_filename


def install_problem_set_host_python(directory):
    """
    Installs the given directory as a problem set,
    for the current python interpreter.
    """

    if not os.path.isdir(directory):
        raise ValueError(f"not a directory: '{directory}'")

    directory = os.path.abspath(directory)

    pth_filename = get_pth_filename()
    try:
        with open(pth_filename, "x") as pth_file:
            logger.info(f"Created new .pth file: {pth_filename}")
            print(PTH_HEADER, file=pth_file)
    except FileExistsError:
        pass

    with open(pth_filename, "a") as pth_file:
        logger.info(f"Appending '{directory}' to existing .pth file: {pth_filename}")
        print(directory, file=pth_file)


def uninstall_host_python():
    pth_filename = get_pth_filename()
    with open(pth_filename, "r") as pth_file:
        if pth_file.readline(len(PTH_HEADER)) != PTH_HEADER:
            raise ValueError(f"File {pth_filename} is not a valid turingarena .pth file")
        logger.info(f"Removing .pth file: {pth_filename}")
        os.unlink(pth_filename)


@docopt_cli
def install_cli(args):
    """
    Usage:
        install <directory>
    """

    directory = args["<directory>"]
    install_problem_set_host_python(directory)


@docopt_cli
def uninstall_cli(args):
    """
    Usage:
        uninstall
    """
    uninstall_host_python()
