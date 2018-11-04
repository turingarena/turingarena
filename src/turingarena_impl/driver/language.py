import importlib
import os
import pkgutil
from collections import namedtuple


class UnknownFileExtension(Exception):
    pass


class Language(namedtuple("Language", [
    "name",
    "extension",
    "ProgramRunner",
    "skeleton_generator",
    "template_generator",
    "supported_for_evaluator",
])):
    __slots__ = []

    @staticmethod
    def languages():
        from . import languages as language_package

        languages = []
        for mod in pkgutil.iter_modules(language_package.__path__):
            mod = importlib.import_module(f"{language_package.__name__}.{mod.name}")
            try:
                languages.append(getattr(mod, "language"))
            except AttributeError:
                pass
        return languages

    @classmethod
    def from_name(cls, name):
        for language in cls.languages():
            if language.name.lower() == name.lower():
                return language
        raise ValueError(f"language {name} not supported by TuringArena")

    @classmethod
    def from_extension(cls, extension):
        for language in cls.languages():
            if language.extension == extension:
                return language
        raise UnknownFileExtension

    @staticmethod
    def from_source_path(source_path):
        base, ext = os.path.splitext(source_path)
        return Language.from_extension(ext)
