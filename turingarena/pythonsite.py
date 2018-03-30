import logging
import os
import site
from distutils.sysconfig import get_python_lib

from turingarena.cli import docopt_cli
from turingarena.config import get_install_dirs

logger = logging.getLogger(__name__)


def configure_turingarena_host_python():
    # should be: prefix, *_ = site.getsitepackages()
    # but it fails due to: https://github.com/pypa/virtualenv/issues/355
    packages_dir = get_python_lib()
    pth_filename = os.path.join(packages_dir, "turingarena.pth")
    logger.info(f"writing file {pth_filename}")
    with open(pth_filename, "w") as f:
        print("# TURINGARENA", file=f)
        print(f"import {__name__}", file=f)


def add_turingarena_packages():
    for d in get_install_dirs():
        site.addsitedir(d)


@docopt_cli
def configure_python_site_cli(args):
    """
    Usage:
        pythonsite
    """
    configure_turingarena_host_python()


# add turingarena folders as Python site dirs
add_turingarena_packages()
