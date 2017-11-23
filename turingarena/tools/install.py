import logging
import subprocess

import os

from turingarena.tools.utils import indent, write_to_file

logger = logging.getLogger(__name__)


def install_with_setuptools(dest_dir, **kwargs):
    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield f"setup("
        for kw, arg in kwargs.items():
            yield indent(f"{kw}={repr(arg)},")
        yield f")"

    setup_py_path = os.path.join(
        dest_dir,
        "setup.py",
    )

    with open(setup_py_path, "w") as setup_py_file:
        write_to_file(generate_setup_py(), setup_py_file)

    subprocess.run(
        ["python", "setup.py", "install", "--force"],
        cwd=dest_dir,
    )
