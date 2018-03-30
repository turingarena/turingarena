import logging
import os
import sys

from turingarena.cli import docopt_cli

logger = logging.getLogger(__name__)

TURINGARENA_PTH = "turingarena.pth"
PTH_HEADER = "# TURINGARENA PROBLEM SETS"


def get_local_install_dir():
    return os.path.join(os.path.expanduser("~"), ".turingarena")


def get_global_install_dir():
    return os.path.join(sys.prefix, "lib", "turingarena")


def get_install_dirs():
    yield get_local_install_dir()
    yield get_global_install_dir()


def list_turingarena_packages():
    for d in get_install_dirs():
        pth_filename = os.path.join(d, TURINGARENA_PTH)
        if not os.path.exists(pth_filename):
            continue
        with open(pth_filename) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                yield f


def write_installed_directories(directories, globally):
    pth_filename = get_pth_filename(globally)

    os.makedirs(os.path.dirname(pth_filename), exist_ok=True)
    logger.debug(f"writing directories to {pth_filename}")
    with open(pth_filename, "w") as f:
        print(PTH_HEADER, file=f)
        for d in directories:
            print(d, file=f)


def read_installed_directories(globally):
    pth_filename = get_pth_filename(globally)

    if not os.path.exists(pth_filename):
        logger.debug(f"file {pth_filename} does not exist -> no installed directories")
        return []

    with open(pth_filename) as f:
        logger.debug(f"reading directories from {pth_filename}")
        lines = f.read().splitlines(keepends=False)
    if PTH_HEADER not in lines[:1]:
        raise ValueError(f"file {pth_filename} has wrong header")
    return lines[1:]


def install_package(directory, globally=False):
    directory = canonicalize_directory(directory)
    directories = read_installed_directories(globally)

    if directory in directories:
        logger.info(f"directory {directory} already installed, skipping")
        return

    logger.info(f"installing directory {directory}")
    directories.append(directory)

    write_installed_directories(directories, globally)


def uninstall_package(directory, globally=False):
    directory = canonicalize_directory(directory)
    directories = read_installed_directories(globally)

    logger.info(f"uninstalling directory {directory}")
    try:
        directories.remove(directory)
    except ValueError:
        logger.error(f"directory {directory} not installed")
    else:
        write_installed_directories(directories, globally)


def get_pth_filename(globally):
    if globally:
        install_dir = get_global_install_dir()
    else:
        install_dir = get_local_install_dir()
    pth_filename = os.path.join(install_dir, TURINGARENA_PTH)
    return pth_filename


def canonicalize_directory(directory):
    if not os.path.isdir(directory):
        raise ValueError(f"not a directory: '{directory}'")
    directory = os.path.abspath(directory)
    return directory


@docopt_cli
def install_cli(args):
    """
    Usage:
        install [options] <directory>

    Options:
        -g --globally  Install globally.
    """

    install_package(args["<directory>"], globally=args["--globally"])


@docopt_cli
def uninstall_cli(args):
    """
    Usage:
        uninstall [options] <directory>

    Options:
        -g --globally  Install globally.
    """
    uninstall_package(args["<directory>"], globally=args["--globally"])
