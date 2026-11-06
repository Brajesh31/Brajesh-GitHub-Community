#!/usr/bin/env python3
"""Report accounts that follow the owner but are not followed back."""

import argparse
import logging

from community import mutation_report, relationship_data
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
    data = relationship_data(client, settings.username)
    mutation_report(
        "follow", data["followers_not_followed"], client, settings.allow_mutations
    )
    logging.info("Candidates: %s", ", ".join(data["followers_not_followed"]) or "none")


if __name__ == "__main__":
    main()
