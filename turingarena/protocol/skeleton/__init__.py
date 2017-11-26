import logging

import os
import shutil
from tempfile import TemporaryDirectory

from turingarena.common import install_with_setuptools
from turingarena.protocol.packaging import load_protocol, parse_protocol_name
from . import cpp

logger = logging.getLogger(__name__)

languages = {
    "cpp": cpp.generate_skeleton
}


class SkeletonGenerator:
    def __init__(self, protocol, dest_dir):
        self.protocol = protocol
        self.dest_dir = dest_dir

        self.skeleton_dir = os.path.join(self.dest_dir, "skeleton")

        self.generate()

    def generate(self):
        os.makedirs(self.skeleton_dir, exist_ok=True)
        shutil.rmtree(self.skeleton_dir)

        os.mkdir(self.skeleton_dir)
        for interface in self.protocol.body.scope.interfaces.values():
            self.generate_skeleton_interface(interface)

    def generate_skeleton_interface(self, interface):
        interface_dir = self.make_interface_dir(interface)
        os.mkdir(interface_dir)
        for language in languages.keys():
            self.generate_skeleton_language(interface=interface, language=language)

    def generate_skeleton_language(self, *, interface, language):
        language_dir = self.make_language_dir(interface, language)
        os.mkdir(language_dir)
        logger.info(
            "Generating support for interface '{interface}'"
            " and language {language} in dir {dir}".format(
                interface=interface.name,
                language=language,
                dir=language_dir,
            )
        )
        languages[language](
            protocol=self.protocol,
            interface=interface,
            dest_dir=language_dir,
        )

    def make_interface_dir(self, interface):
        return os.path.join(self.skeleton_dir, interface.name)

    def make_language_dir(self, interface, language):
        return os.path.join(self.make_interface_dir(interface), language)


def install_skeleton(protocol_name):
    parts = parse_protocol_name(protocol_name)
    package_name = f"turingarena_skeletons.{protocol_name}"
    protocol = load_protocol(protocol_name)

    with TemporaryDirectory() as dest_dir:
        package_dir = os.path.join(
            dest_dir,
            "turingarena_skeletons",
            *parts,
        )

        SkeletonGenerator(protocol, dest_dir=package_dir)

        with open(os.path.join(package_dir, "__init__.py"), "w") as init_py:
            pass

        levels = 10
        install_with_setuptools(
            dest_dir,
            name=package_name,
            packages=[package_name],
            package_data={
                # copy recursively up to levels
                package_name: ["/".join(["*"] * i) for i in range(1, levels)],
            },
            zip_safe=False,
        )
