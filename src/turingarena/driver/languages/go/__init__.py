from turingarena.driver.language import Language

from .generator import GoCodeGen
from .runner import GoProgramRunner

disabled_language = Language(
    name="Go",
    extension=".go",
    ProgramRunner=GoProgramRunner,
    Generator=GoCodeGen,
    supported_for_evaluator=False,
)
