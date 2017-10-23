import logging
import os
import shutil

logger = logging.getLogger(__name__)

from . import python

languages = {
    "python": python.ProxyGenerator,
}


class ProxyGenerator:
    def __init__(self, *, protocol, dest_dir):
        self.protocol = protocol
        self.dest_dir = dest_dir

        self.proxy_dir = os.path.join(self.dest_dir, "proxy")

        self.generate()

    def generate(self):
        os.makedirs(self.proxy_dir, exist_ok=True)
        shutil.rmtree(self.proxy_dir)
        os.mkdir(self.proxy_dir)

        for language in languages.keys():
            self.generate_language(language)

    def generate_language(self, language):
        language_dir = os.path.join(self.proxy_dir, language)
        os.mkdir(language_dir)
        logger.info(
            "Generating proxy for all protocol for language {language} in dir {dir}".format(
                language=language,
                dir=language_dir,
            )
        )
        languages[language](self.protocol, language_dir)


generate_proxy = ProxyGenerator