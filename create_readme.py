#!/usr/bin/env python3
"""Fetch relationships and generate the project's follower report."""

import argparse
import logging
from datetime import datetime, timezone

from community import relationship_data, write_json
from config import add_common_arguments, settings_from_args
from github_api import GitHubClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    settings = settings_from_args(args)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    client = GitHubClient(settings.token)
    identity = client.verify_token()
    if identity["login"].lower() != settings.username.lower():
        raise SystemExit(
            f"Token belongs to {identity['login']}, not {settings.username}."
        )
    data = relationship_data(client, settings.username)
    profiles = data["follower_profiles"]
    lines = [
        "# GitHub Community Report",
        "",
        f"Analytics for [{settings.username}](https://github.com/{settings.username}).",
        "",
        f"- Followers: **{len(data['followers'])}**",
        f"- Following: **{len(data['following'])}**",
        f"- Mutual relationships: **{len(data['mutual'])}**",
        f"- Follow me, not followed: **{len(data['followers_not_followed'])}**",
        f"- I follow, not following back: **{len(data['following_not_following_back'])}**",
        "",
        f"_Updated {datetime.now(timezone.utc).isoformat(timespec='seconds')}_",
        "",
        "## Followers",
        "",
    ]
    lines.extend(
        f'<a href="https://github.com/{login}"><img src="{avatar}" '
        f'alt="{login}" height="50" width="50"></a>'
        for login, avatar in profiles
    )
    lines.append("")
    from community import atomic_write

    atomic_write("README.md", "\n".join(lines))
    atomic_write("index.html", "\n".join(["<!doctype html>", "<meta charset=\"utf-8\">",
        "<title>GitHub Community Report</title>", "<h1>GitHub Community Report</h1>",
        *[f'<a href="https://github.com/{login}"><img src="{avatar}" alt="{login}" height="50" width="50"></a>' for login, avatar in profiles],
    ]))
    write_json("Dataset.json", profiles)
    write_json("reports/relationships.json", {key: value for key, value in data.items() if key != "follower_profiles"})
    logging.info("Wrote report for %d followers.", len(profiles))


if __name__ == "__main__":
    main()
