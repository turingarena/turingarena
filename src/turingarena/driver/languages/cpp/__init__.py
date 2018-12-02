from turingarena.driver.language import Language

from .generator import CppCodeGen
from .runner import CppProgramRunner

language = Language(
    name="C++",
    extension=".cpp",
    ProgramRunner=CppProgramRunner,
    Generator=CppCodeGen,
    supported_for_evaluator=True,
)
