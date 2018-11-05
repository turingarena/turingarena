from turingarena.driver.language import Language
from .generator import BashSkeletonCodeGen, BashTemplateCodeGen
from .runner import BashProgramRunner

# language = Language(
#     name="Bash",
#     extension=".sh",
#     ProgramRunner=BashProgramRunner,
#     skeleton_generator=BashSkeletonCodeGen,
#     template_generator=BashTemplateCodeGen,
#     supported_for_evaluator=False,
# )
