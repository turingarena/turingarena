import logging
import os
import shutil
from tempfile import TemporaryDirectory

import subprocess

from turingarena.tools.utils import write_to_file
from turingarena.tools.install import install_with_setuptools

logger = logging.getLogger(__name__)


def install_protocol(protocol_id):
    package_name = protocol_id.python_package()
    filename = "__init__.tap"

    with TemporaryDirectory() as dest_dir:
        package_dir = os.path.join(
            dest_dir,
            protocol_id.python_package_dir(),
        )
        os.makedirs(package_dir)

        shutil.copy(
            protocol_id.source_path(),
            os.path.join(package_dir, filename),
        )
        with open(os.path.join(package_dir, "__init__.py"), "w") as init_py:
            pass

        install_with_setuptools(
            dest_dir,
            name=package_name,
            packages=[package_name],
            package_data={
                package_name: [filename],
            },
            zip_safe=False,
        )