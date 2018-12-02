from turingarena.driver.languages.cpp import CppCodeGen


class CCodeGen(CppCodeGen):
    def generate_method_declarations(self, interface):
        self.line('extern "C" {')
        for func in interface.methods:
            with self.indent():
                self.method_declaration(func)
        self.line("}")
