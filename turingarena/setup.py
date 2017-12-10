import os
import shutil
import sys
from tempfile import TemporaryDirectory

from turingarena.modules import parse_module_name, python_module_parts
from turingarena.protocol.model.exceptions import ProtocolError
from turingarena.protocol.module import PROTOCOL_QUALIFIER, compile_protocol
from turingarena.protocol.proxy.python import generate_proxy
from turingarena.protocol.skeleton import generate_skeleton


def turingarena_setup(*, source_dir=".", name, protocols):
    from turingarena.common import install_with_setuptools
    from turingarena.modules import MODULES_PACKAGE
    from turingarena.modules import module_to_python_package
    from turingarena.protocol.module import PROTOCOL_QUALIFIER

    python_packages = []
    with TemporaryDirectory() as dest_dir:
        for protocol_name in protocols:
            python_packages.append(module_to_python_package(PROTOCOL_QUALIFIER, protocol_name))
            _prepare_protocol(dest_dir, protocol_name, source_dir)
        levels = 5
        install_with_setuptools(
            dest_dir,
            name=f"{MODULES_PACKAGE}.{name}",
            packages=python_packages,
            package_data={
                # copy recursively up to levels
                package_name: ["/".join(["*"] * i) for i in range(1, levels)]
                for package_name in python_packages
            },
            zip_safe=False,
        )


def _prepare_protocol(dest_dir, protocol_name, source_dir):
    module_dir = _prepare_module_dir(dest_dir, PROTOCOL_QUALIFIER, protocol_name)
    parts = parse_module_name(protocol_name)
    source_filename = os.path.join(source_dir, *parts[:-1], f"{parts[-1]}.tap")
    with open(source_filename) as f:
        protocol_text = f.read()
    try:
        protocol = compile_protocol(protocol_text, filename=source_filename)
    except ProtocolError as e:
        sys.exit(e.get_user_message())

    dest_source_filename = os.path.join(module_dir, "_source.tap")
    shutil.copy(
        source_filename,
        dest_source_filename,
    )

    generate_proxy(module_dir, protocol)
    generate_skeleton(protocol, dest_dir=os.path.join(module_dir, "_skeletons"))


def _prepare_module_dir(dest_dir, qualifier, name):
    module_dir = os.path.join(
        dest_dir,
        *python_module_parts(qualifier, name),
    )
    os.makedirs(module_dir, exist_ok=True)
    with open(os.path.join(module_dir, "__init__.py"), "x"):
        pass
    return module_dir