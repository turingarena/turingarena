"""Naval Fate.

Usage:
  taskrun [--maxproc=<maxproc>]
  taskrun (-h | --help)
  taskrun --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  --maxproc=<maxproc>  Speed in knots [default: 20].
"""

from docopt import docopt

def main():
    print(docopt(__doc__))
