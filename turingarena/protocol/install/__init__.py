import os
import shutil
from tempfile import TemporaryDirectory

from gevent import subprocess

from turingarena.protocol.codegen.utils import write_to_file


def install_protocol(protocol_id):
    qual_package_name = protocol_id.python_package()

    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield f"setup("
        yield f"    name='{qual_package_name}',"
        yield f"    packages=['{qual_package_name}'],"
        yield f")"

    with TemporaryDirectory() as dest_dir:
        package_dir = os.path.join(
            dest_dir,
            protocol_id.python_package_dir(),
        )
        os.makedirs(package_dir)

        setup_py_path = os.path.join(
            dest_dir,
            "setup.py",
        )

        shutil.copy(
            protocol_id.source_path(),
            os.path.join(package_dir, "__init__.tap"),
        )

        with open(setup_py_path, "w") as setup_py_file:
            write_to_file(generate_setup_py(), setup_py_file)

        subprocess.run(
            ["python", "setup.py", "install"],
            chdir=dest_dir,
        )

