from turingarena.driver.languages.cpp import CppSkeletonCodeGen, CppTemplateCodeGen


class CSkeletonCodeGen(CppSkeletonCodeGen):
    def generate_method_declarations(self, interface):
        yield 'extern "C" {'
        for func in interface.methods:
            yield from self.indent_all(self.generate_method_declaration(func))
        yield "}"


class CTemplateCodeGen(CppTemplateCodeGen):
    pass
