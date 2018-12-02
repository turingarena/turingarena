from turingarena.driver.language import Language

from .generator import CCodeGen
from .runner import CProgramRunner

language = Language(
    name="C",
    extension=".c",
    ProgramRunner=CProgramRunner,
    Generator=CCodeGen,
    supported_for_evaluator=False,
)
