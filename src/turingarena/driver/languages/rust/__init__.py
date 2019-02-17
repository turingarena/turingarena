from turingarena.driver.language import Language

from .generator import RustCodeGen
from .runner import RustProgramRunner

language = Language(
    name="Rust",
    extension=".rs",
    ProgramRunner=RustProgramRunner,
    Generator=RustCodeGen,
    supported_for_evaluator=False,
)
