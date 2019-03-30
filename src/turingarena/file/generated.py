import os
from functools import lru_cache

from turingarena.driver.compile.compile import compile_interface
from turingarena.driver.language import Language
from turingarena.text.parser import TextParser

INTERFACE_TXT = "interface.txt"
TEXT_FILENAME = "statement.md"


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
        return list(
            (os.path.normpath(path), gen)
            for path, gen in self._generate_targets()
        )

    def _create_text_generator(self, path):
        def generate(outfile):
            with open(path) as f:
                outfile.write(f.read())

        return generate

    def _generate_targets(self):
        for dirpath, dirnames, filenames in os.walk(self.work_dir):
            relpath = os.path.relpath(dirpath, self.work_dir)
            descriptions = {}
            if TEXT_FILENAME in filenames:
                text_path = os.path.join(dirpath, TEXT_FILENAME)
                descriptions = TextParser(text_path).descriptions
                yield (os.path.join(relpath, TEXT_FILENAME), self._create_text_generator(text_path))
            if INTERFACE_TXT in filenames:
                yield from self._generate_interface_targets(dirpath, relpath, descriptions)

    def _generate_interface_targets(self, abspath, relpath, descriptions):
        interface_path = os.path.join(abspath, INTERFACE_TXT)
        yield (os.path.join(relpath, INTERFACE_TXT)), self._create_text_generator(interface_path)
        for lang in self.languages:
            yield (
                os.path.join(relpath, lang.name, f"skeleton{lang.extension}"),
                self._create_interface_code_generator(interface_path, descriptions, lang.Generator()),
            )
            yield (
                os.path.join(relpath, lang.name, f"template{lang.extension}"),
                self._create_interface_code_generator(interface_path, descriptions, lang.Generator(), template=True),
            )

    def _create_interface_code_generator(self, interface_path, descriptions, code_generator, template=False):
        def generator(outfile):
            with open(interface_path) as f:
                interface = compile_interface(f.read())

            if template:
                code_generator.generate_template_to_file(interface, descriptions, outfile)
            else:
                code_generator.generate_to_file(interface, outfile)

        return generator

    def cat_file(self, path, *, file):
        path = os.path.normpath(path)
        for p, generator in self.targets:
            if p == path:
                generator(file)
                return
        raise FileNotFoundError(path)
