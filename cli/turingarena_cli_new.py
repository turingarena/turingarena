from __future__ import print_function

import argparse


def main():
    parser = argparse.ArgumentParser(description="Turingarena CLI")
    parser.add_mutually_exclusive_group()
    parser.add_argument("make", help="compile all files of the problem")
    parser.add_argument("evaluate", help="evaluate a submission")
    args = parser.parse_args()
    print(args)

if __name__ == "__main__":
    main()