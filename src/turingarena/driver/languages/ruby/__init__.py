from turingarena.driver.language import Language

from .generator import RubyCodeGen
from .runner import RubyProgramRunner

language = Language(
    name="Ruby",
    extension=".rb",
    ProgramRunner=RubyProgramRunner,
    Generator=RubyCodeGen,
    supported_for_evaluator=True,
)
