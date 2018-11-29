import os
from functools import lru_cache

from turingarena.driver.interface.compile import Compiler
from turingarena.driver.language import Language
from turingarena.text.parser import TextParser

INTERFACE_TXT = "interface.txt"
TEXT_FILENAMES = ["statement.md", "README.md"]


class PackGeneratedDirectory:

    def __init__(self, work_dir, allowed_languages=None):
        self.work_dir = work_dir
        if allowed_languages is None:
            self.languages = Language.languages()
        else:
            self.languages = [
                Language.from_name(name)
                for name in allowed_languages
            ]

    @property
    @lru_cache(None)
    def targets(self):
        return list(self._generate_targets())

    def _create_text_generator(self, path):
        def generate(outfile):
            with open(path) as f:
                outfile.write(f.read())

        return generate

    def _generate_targets(self):
        for dirpath, dirnames, filenames in os.walk(self.work_dir):
            relpath = os.path.relpath(dirpath, self.work_dir)
            descriptions = {}
            for file in TEXT_FILENAMES:
                if file in filenames:
                    text_path = os.path.join(dirpath, file)
                    descriptions = TextParser(text_path).descriptions
                    yield (os.path.join(relpath, TEXT_FILENAMES[0]), self._create_text_generator(text_path))
                    break
            if INTERFACE_TXT in filenames:
                yield from self._generate_interface_targets(dirpath, relpath, descriptions)

    def _generate_interface_targets(self, abspath, relpath, descriptions):
        for lang in self.languages:
            interface_path = os.path.join(abspath, INTERFACE_TXT)
            yield (
                os.path.join(relpath, lang.name, f"skeleton{lang.extension}"),
                self._create_interface_code_generator(interface_path, descriptions, lang.skeleton_generator()),
            )
            yield (
                os.path.join(relpath, lang.name, f"template{lang.extension}"),
                self._create_interface_code_generator(interface_path, descriptions, lang.template_generator()),
            )

    def _create_interface_code_generator(self, interface_path, descriptions, code_generator):
        def generator(outfile):
            with open(interface_path) as f:
                interface = Compiler.create().compile(f.read(), descriptions=descriptions)

            code_generator.generate_to_file(interface, outfile)

        return generator

    def cat_file(self, path, *, file):
        for p, generator in self.targets:
            if os.path.normpath(p) == os.path.normpath(path):
                return generator(file)
        raise FileNotFoundError(path)
