from turingarena.driver.language import Language
from .generator import BashCodeGen
from .runner import BashProgramRunner

disabled_language = Language(
    name="Bash",
    extension=".sh",
    ProgramRunner=BashProgramRunner,
    Generator=BashCodeGen,
    supported_for_evaluator=False,
)
