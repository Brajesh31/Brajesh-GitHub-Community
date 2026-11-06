#!/usr/bin/env python3
"""Report and optionally follow accounts that follow Brajesh31 back."""

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
    results = execute_mutations(client, data["followers_not_followed"], "follow", settings, "follow-back")
    logging.info("Follow-back candidates: %d; successful actions: %d", len(data["followers_not_followed"]), sum(r["status"] == "success" for r in results))


if __name__ == "__main__":
    main()
