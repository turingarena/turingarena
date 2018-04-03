from collections import namedtuple


class Language(namedtuple("Language", [
    "name",
    "extension",
    "source",
    "executable",
    "skeleton_generator",
    "template_generator",
])):

    @staticmethod
    def for_name(name):
        from .cpp import language as cpp
        from .java import language as java
        from .javascript import language as javascript
        from .python import language as python

        languages = {
            "c++": cpp,
            "java": java,
            "javascript": javascript,
            "python": python,
        }

        try:
            return languages[name]
        except KeyError:
            raise RuntimeError(f"Language {language} not supported by TuringArena")
