import os

from collections import namedtuple

from turingarena.driver.language import Language, UnknownFileExtension


class SubmissionFile(namedtuple("SubmissionFile", ["filename", "content"])):
    @property
    def extension(self):
        return os.path.splitext(self.filename)[1]

    @property
    def language(self):
        try:
            return Language.from_extension(self.extension)
        except UnknownFileExtension:
            return None
