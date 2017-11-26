import logging

import os
import shutil
from tempfile import TemporaryDirectory

from turingarena.common import install_with_setuptools
from turingarena.protocol.packaging import parse_protocol_name

logger = logging.getLogger(__name__)


def install_protocol(protocol_name):
    parts = parse_protocol_name(protocol_name)

    package_name = f"turingarena_protocols.{protocol_name}"
    filename = "__init__.tap"

    with TemporaryDirectory() as dest_dir:
        package_dir = os.path.join(
            dest_dir,
            "turingarena_protocols",
            *parts,
        )
        os.makedirs(package_dir)

        shutil.copy(
            os.path.join(*parts[:-2], f"{parts[-1]}.tap"),
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
