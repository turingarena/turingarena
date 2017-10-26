import logging
import os

logger = logging.getLogger(__name__)

from . import python

languages = {
    "python": python.generate_proxy,
}


def generate_proxy(*, protocol, dest_dir, language):
    os.makedirs(dest_dir, exist_ok=True)
    logger.info(
        "Generating proxy for language {language} in dir {dir}".format(
            language=language,
            dir=dest_dir,
        )
    )
    languages[language](protocol, dest_dir=dest_dir)
