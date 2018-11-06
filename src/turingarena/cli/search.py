import sys
from argparse import ArgumentParser

import requests

from turingarena.cli.base import BASE_PARSER
from turingarena.cli.command import Command

GITHUB_SEARCH_ENDPOINT = "https://api.github.com/search/repositories"


class SearchCommand(Command):
    PARSER = ArgumentParser(
        description="Search for a TuringArena tasks in the repository",
        parents=[BASE_PARSER],
        add_help=False,
    )

    PARSER.add_argument("query", nargs="*")

    def run(self):
        sys.stdout.write("Searching...")
        sys.stdout.flush()

        res = requests.get(GITHUB_SEARCH_ENDPOINT
                           + "?q="
                           + "topic:turingarena+"
                           + "+".join(self.args.query)).json()

        sys.stdout.write("\b" * 12)

        print("%d%s result%s found%s" % (
            res["total_count"],
            "+" if res["incomplete_results"] else "",
            "s" if res["total_count"] != 1 else "",
            ":" if res["total_count"] > 0 else "."))

        for item in res["items"]:
            print("- {full_name:<30} {description}".format(**item))
