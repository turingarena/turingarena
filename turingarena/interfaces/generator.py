import logging
import os
import shutil

import turingarena.interfaces.drivergen.python.main as python_drivergen
import turingarena.interfaces.supportgen.cpp.main as cpp_supportgen

logger = logging.getLogger(__name__)

lang_supportgen = {
    "cpp": cpp_supportgen.SupportGenerator
}

lang_drivergen = {
    "python": python_drivergen.DriverGenerator,
}


class CodeGenerator:
    def __init__(self, task, output_dir):
        self.task = task
        self.output_dir = output_dir

        self.interfaces_dir = os.path.join(self.output_dir, "interfaces")
        self.runtime_dir = os.path.join(self.output_dir, "runtime")

    def generate(self):
        os.makedirs(self.output_dir, exist_ok=True)

        # cleanup
        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.mkdir(self.output_dir)

        self.generate_interfaces_support()
        self.generate_driver()

    def generate_interfaces_support(self):
        os.mkdir(self.interfaces_dir)
        for interface in self.task.interfaces:
            self._generate_support_for(interface)

    def _generate_support_for(self, interface):
        interface_dir = os.path.join(self.interfaces_dir, interface.name)
        os.mkdir(interface_dir)
        for language, generator in lang_supportgen.items():
            self._generate_support_language(generator, interface, interface_dir, language)

    def _generate_support_language(self, generator, interface, interface_dir, language):
        language_dir = os.path.join(interface_dir, language)
        os.mkdir(language_dir)
        logger.info(
            "Generating support for interface '{interface}'"
            " and language {language} in dir {dir}".format(
                interface=interface.name,
                language=language,
                dir=language_dir,
            )
        )
        generator(self.task, interface, language_dir)

    def generate_driver(self):
        os.mkdir(self.runtime_dir)
        for language, generator in lang_drivergen.items():
            self._generate_driver_language(generator, language)

    def _generate_driver_language(self, generator, language):
        language_dir = os.path.join(self.runtime_dir, language)
        os.mkdir(language_dir)
        logger.info(
            "Generating driver for all interfaces for language {language} in dir {dir}".format(
                language=language,
                dir=language_dir,
            )
        )
        generator(self.task, language_dir)
