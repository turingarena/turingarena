from turingarena.driver.language import Language

from .generator import JavaCodeGen
from .runner import JavaProgramRunner

disabled_language = Language(
    name="Java",
    extension=".java",
    ProgramRunner=JavaProgramRunner,
    Generator=JavaCodeGen,
    supported_for_evaluator=False,
)
