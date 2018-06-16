from turingarena_impl.sandbox.languages.language import Language
from .generator import JavaScriptSkeletonCodeGen, JavaScriptTemplateCodeGen
from .source import JavascriptAlgorithmSource

language = Language(
    name="javascript",
    extension=".js",
    source=JavascriptAlgorithmSource,
    skeleton_generator=JavaScriptSkeletonCodeGen,
    template_generator=JavaScriptTemplateCodeGen,
)
