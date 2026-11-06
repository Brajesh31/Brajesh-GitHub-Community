#!/usr/bin/env python3
"""Follow eligible discovered candidates only when explicitly enabled."""

import argparse
import logging

from community import execute_mutations, paths, read_json, write_json, write_lines
from config import add_common_arguments, load_names, settings_from_args
from github_api import GitHubClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    settings = settings_from_args(args)
    settings.configure_logging()
    client = GitHubClient(settings.token)
    client.require_identity(settings.username)
    following = {u["login"].lower() for u in client.users("following", settings.username)}
    blacklist = load_names(settings.blacklist_path)
    try:
        queue = [line.strip() for line in open("new_users_list.txt", encoding="utf-8") if line.strip()]
    except FileNotFoundError:
        queue = [item["username"] for item in read_json(paths(settings.data_dir)["candidates.json"], [])]
    eligible = [name for name in queue if name.lower() not in following and name.lower() not in blacklist]
    results = execute_mutations(client, eligible, "follow", settings, "discovery")
    successful = {item["username"].lower() for item in results if item["status"] == "success"}
    remaining = [name for name in eligible if name.lower() not in successful]
    write_lines("new_users_list.txt", remaining)
    candidates = [item for item in read_json(paths(settings.data_dir)["candidates.json"], [])
                  if item.get("username", "").lower() not in successful]
    write_json(paths(settings.data_dir)["candidates.json"], candidates)
    logging.info(
        "Processed %d candidates; %d succeeded; %d failed.",
        len(results),
        len(successful),
        sum(item["status"] == "failed" for item in results),
    )


if __name__ == "__main__":
    main()
