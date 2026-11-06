#!/usr/bin/env python3
"""Maintain a deduplicated queue of public accounts for later review."""

import argparse
import logging

from community import write_lines
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
    following = {user["login"] for user in client.paged(f"/users/{settings.username}/following")}
    existing = set()
    try:
        with open("new_users_list.txt", encoding="utf-8") as handle:
            existing = {line.strip() for line in handle if line.strip()}
    except FileNotFoundError:
        pass
    discovered = {
        user["login"]
        for user in client.paged("/users", max_pages=10)
        if user.get("login")
    }
    queue = sorted((existing | discovered) - following - {settings.username})
    write_lines("new_users_list.txt", queue)
    logging.info("Maintained %d unique review candidates.", len(queue))


if __name__ == "__main__":
    main()
