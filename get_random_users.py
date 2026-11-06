#!/usr/bin/env python3
"""Discover public accounts into a persistent, reviewable candidate queue."""

import argparse
import logging
from datetime import datetime, timezone

from community import followed_history, paths, read_json, write_json, write_lines
from config import add_common_arguments, load_names, settings_from_args
from github_api import GitHubClient


def merge_candidates(users, existing, username, following, blacklist, completed):
    by_login = {
        item["username"].lower(): item for item in existing
        if isinstance(item, dict) and item.get("username")
    }
    for user in users:
        login = user.get("login", "")
        lower = login.lower()
        if not login or lower in {username.lower(), *following, *blacklist, *completed}:
            continue
        by_login.setdefault(lower, {
            "username": login,
            "avatar_url": user.get("avatar_url", ""),
            "profile_url": user.get("html_url", ""),
            "type": user.get("type", "User"),
            "discovered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "awaiting_review",
        })
    return sorted(by_login.values(), key=lambda item: item["username"].lower())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    settings = settings_from_args(args)
    settings.configure_logging()
    if not settings.auto_discovery_enabled:
        logging.info("Discovery is disabled.")
        return
    client = GitHubClient(settings.token)
    client.require_identity(settings.username)
    following = {u["login"].lower() for u in client.users("following", settings.username)}
    blacklist = load_names(settings.blacklist_path)
    completed = followed_history(settings.data_dir)
    candidates = read_json(paths(settings.data_dir)["candidates.json"], [])
    queue = merge_candidates(
        client.public_users(max_pages=10), candidates, settings.username,
        following, blacklist, completed
    )
    write_json(paths(settings.data_dir)["candidates.json"], queue)
    write_lines("new_users_list.txt", [item["username"] for item in queue])
    logging.info("Maintained %d candidates.", len(queue))


if __name__ == "__main__":
    main()
