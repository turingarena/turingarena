import os
import random
import runpy

import sys

from turingarena.logging_helper import init_logger


def main():
    random.seed(os.environ.get("TURINGARENA_SEED", None))

    init_logger()

    evaluator_path = sys.argv[1]
    sys.argv.pop(1)
    runpy.run_path(evaluator_path, run_name="__main__")


if __name__ == '__main__':
    main()
