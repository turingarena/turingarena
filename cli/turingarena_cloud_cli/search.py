from argparse import ArgumentParser

import requests

from .base import BASE_PARSER
from .command import Command

GITHUB_SEARCH_ENDPOINT = "https://api.github.com/search/repositories"


class SearchCommand(Command):
    PARSER = ArgumentParser(
        description="Search for a TuringArena tasks in the repository",
        parents=[BASE_PARSER],
        add_help=False,
    )

    PARSER.add_argument("query", nargs="*")

    def run(self):
        print("Searching...", end="", flush=True)

        response = requests.get("{}?q=topic:turingarena+{}".format(GITHUB_SEARCH_ENDPOINT, "+".join(self.args.query)))
        response_json = response.json()

        print("\b" * 12, end="", flush=True)

        print("{}{} result{} found{}".format(
            response_json["total_count"],
            "+" if response_json["incomplete_results"] else "",
            "s" if response_json["total_count"] > 1 else "",
            ":" if response_json["total_count"] > 0 else ".",
        ))

        for item in response_json["items"]:
            print("- {full_name:<30} {description}".format(**item))
