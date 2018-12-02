from turingarena.driver.language import Language
from turingarena.driver.languages.python.generator import PythonCodeGen

from .generator import PythonCodeGen
from .runner import PythonProgramRunner

language = Language(
    name="Python",
    extension=".py",
    ProgramRunner=PythonProgramRunner,
    Generator=PythonCodeGen,
    supported_for_evaluator=True,
)
