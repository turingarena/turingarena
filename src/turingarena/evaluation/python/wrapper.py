import os
import random
import runpy

import sys


def main():
    random.seed(os.environ.get("TURINGARENA_SEED", None))

    evaluator_path = sys.argv[1]
    sys.argv.pop(1)
    runpy.run_path(evaluator_path)


if __name__ == '__main__':
    main()
