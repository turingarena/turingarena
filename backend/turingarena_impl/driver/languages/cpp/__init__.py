from turingarena_impl.driver.languages.language import Language
from .generator import CppSkeletonCodeGen, CppTemplateCodeGen
from .source import CppAlgorithmSource

language = Language(
    name="c++",
    extension=".cpp",
    source=CppAlgorithmSource,
    skeleton_generator=CppSkeletonCodeGen,
    template_generator=CppTemplateCodeGen,
)
