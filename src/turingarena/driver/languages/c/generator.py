from turingarena.driver.languages.cpp import CppSkeletonCodeGen, CppTemplateCodeGen


class CSkeletonCodeGen(CppSkeletonCodeGen):
    def generate_method_declarations(self, interface):
        yield 'extern "C" {'
        for func in interface.methods:
            with self.indent():
                yield from self.visit_MethodPrototype(func)
        yield "}"


class CTemplateCodeGen(CppTemplateCodeGen):
    pass
