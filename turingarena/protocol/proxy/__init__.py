import logging
import os

logger = logging.getLogger(__name__)

from . import python

languages = {
    "python": python.generate_proxy,
}


def generate_proxy(*, protocol_name, language):
    logger.info(
        f"Installing proxy for protocol {protocol_name} language {language}"
    )
    languages[language](protocol_name)
