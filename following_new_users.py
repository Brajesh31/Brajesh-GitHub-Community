#!/usr/bin/env python3
"""Report queued accounts; following is opt-in via --allow-mutations."""

import argparse
import logging

from community import mutation_report
from config import add_common_arguments, settings_from_args
from github_api import GitHubClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    settings = settings_from_args(args)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    client = GitHubClient(settings.token)
    client.verify_token()
    try:
        with open("new_users_list.txt", encoding="utf-8") as handle:
            candidates = [line.strip() for line in handle if line.strip()]
    except FileNotFoundError:
        candidates = []
    mutation_report("follow", candidates, client, settings.allow_mutations)
    logging.info("Queued candidates: %d", len(candidates))


if __name__ == "__main__":
    main()
