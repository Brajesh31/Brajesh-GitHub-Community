#!/usr/bin/env python3
"""Report and optionally unfollow eligible non-mutual accounts."""

import argparse
import logging

from community import execute_mutations, relationship_data
from config import add_common_arguments, settings_from_args
from github_api import GitHubClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    settings = settings_from_args(args)
    settings.configure_logging()
    client = GitHubClient(settings.token)
    client.require_identity(settings.username)
    data = relationship_data(client, settings.username)
    results = execute_mutations(client, data["following_not_following_back"], "unfollow", settings, "unfollow")
    logging.info("Unfollow candidates: %d; successful actions: %d", len(data["following_not_following_back"]), sum(r["status"] == "success" for r in results))


if __name__ == "__main__":
    main()
