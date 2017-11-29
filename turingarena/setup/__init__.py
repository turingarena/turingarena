from tempfile import TemporaryDirectory


def turingarena_setup(*, source_dir=".", name, protocols):
    from turingarena.common import install_with_setuptools
    from turingarena.setup.common import module_to_python_package, MODULES_PACKAGE, PROTOCOL_QUALIFIER
    from turingarena.setup.setup import _prepare_protocol

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
