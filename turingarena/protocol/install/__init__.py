import logging
import os
import shutil
from tempfile import TemporaryDirectory

import subprocess

from turingarena.protocol.codegen.utils import write_to_file

logger = logging.getLogger(__name__)


def install_protocol(protocol_id):
    package_name = protocol_id.python_package()
    filename = "__init__.tap"

    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield f"setup("
        yield f"    name='{package_name}',"
        yield f"    packages={[package_name]},"
        yield f"    package_data={dict([(package_name, [filename])])},"
        yield f"    zip_safe={False},"
        yield f")"

    with TemporaryDirectory() as dest_dir:
        package_dir = os.path.join(
            dest_dir,
            protocol_id.python_package_dir(),
        )
        os.makedirs(package_dir)

        logger.debug(f"{locals()}")
        setup_py_path = os.path.join(
            dest_dir,
            "setup.py",
        )

        shutil.copy(
            protocol_id.source_path(),
            os.path.join(package_dir, filename),
        )

        logger.debug(f"writing {setup_py_path}...")
        with open(setup_py_path, "w") as setup_py:
            write_to_file(generate_setup_py(), setup_py)

        with open(os.path.join(package_dir, "__init__.py"), "w") as init_py:
            pass

        # DEBUG
        subprocess.run(["find"], cwd=dest_dir)
        subprocess.run(["cat", "setup.py"], cwd=dest_dir)

        cmd = ["python", "setup.py", "install", "--force"]
        logger.debug(f"running {cmd} in dir {dest_dir}...")
        subprocess.run(
            cmd,
            cwd=dest_dir,
        )
