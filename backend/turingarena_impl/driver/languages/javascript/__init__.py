from turingarena_impl.driver.language import Language
from .generator import JavaScriptSkeletonCodeGen, JavaScriptTemplateCodeGen
from .source import JavascriptAlgorithmSource

# TODO: temporarily disable because there are errors in skeleton and template generators.
# language = Language(
#     name="javascript",
#     extension=".js",
#     source=JavascriptAlgorithmSource,
#     skeleton_generator=JavaScriptSkeletonCodeGen,
#     template_generator=JavaScriptTemplateCodeGen,
# )
