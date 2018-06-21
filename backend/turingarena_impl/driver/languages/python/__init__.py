from turingarena_impl.driver.languages.language import Language
from .generator import PythonSkeletonCodeGen, PythonTemplateCodeGen
from .source import PythonAlgorithmSource

language = Language(
    name="python",
    extension=".py",
    source=PythonAlgorithmSource,
    skeleton_generator=PythonSkeletonCodeGen,
    template_generator=PythonTemplateCodeGen,
)
