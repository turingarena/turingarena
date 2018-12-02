from turingarena.driver.common.nodes import *
from turingarena.driver.common.transform import TreeTransformer


class CompilationPostprocessor(TreeTransformer):
    def transform_Interface(self, n):
        return super().transform_Interface(n._replace(
            main_block=n.main_block._replace(
                children=(Checkpoint(),) + n.main_block.children + (Exit(),),
            ),
        ))
