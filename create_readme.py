#!/usr/bin/env python3
"""Generate deduplicated README, JSON reports, and dashboard data."""

import argparse
from datetime import datetime, timezone

from community import atomic_write, paths, read_json, relationship_data, write_json
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
    profiles = data["follower_profiles"]
    candidate_data = read_json(paths(settings.data_dir)["candidates.json"], [])
    action_data = read_json(paths(settings.data_dir)["action_history.json"], [])
    successful_follows = [a for a in action_data if a.get("action") == "follow" and a.get("status") == "success"]
    stats = {
        "username": settings.username,
        "followers": len(data["followers"]),
        "following": len(data["following"]),
        "mutual": len(data["mutual"]),
        "followers_not_followed": len(data["followers_not_followed"]),
        "following_not_following_back": len(data["following_not_following_back"]),
        "discovered_candidates": len(candidate_data),
        "successfully_followed": len(successful_follows),
        "awaiting_review": sum(item.get("status") == "awaiting_review" for item in candidate_data),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    generated = [
        "<!-- COMMUNITY_REPORT_START -->",
        "## Generated community report", "",
        f"Community analytics for [{settings.username}](https://github.com/{settings.username}).", "",
        "## Community statistics", "",
        *[f"- {key.replace('_', ' ').title()}: **{value}**" for key, value in stats.items() if key not in {"username", "updated_at"}],
        f"- Updated: `{stats['updated_at']}`", "",
        "## Followers", "",
        *[f'<a href="https://github.com/{login}"><img src="{avatar}" alt="{login}" height="50" width="50"></a>' for login, avatar in profiles],
        "",
        "<!-- COMMUNITY_REPORT_END -->", "",
    ]
    existing_readme = ""
    try:
        with open("README.md", encoding="utf-8") as handle:
            existing_readme = handle.read()
    except FileNotFoundError:
        existing_readme = f"# Brajesh GitHub Community\n\nCommunity analytics for {settings.username}.\n"
    start = existing_readme.find("<!-- COMMUNITY_REPORT_START -->")
    end = existing_readme.find("<!-- COMMUNITY_REPORT_END -->")
    if start >= 0 and end >= start:
        readme = existing_readme[:start] + "\n".join(generated) + existing_readme[end + len("<!-- COMMUNITY_REPORT_END -->"):]
    else:
        readme = existing_readme.rstrip() + "\n\n" + "\n".join(generated)
    atomic_write("README.md", readme)
    write_json("Dataset.json", profiles)
    write_json("reports/relationships.json", {key: value for key, value in data.items() if key != "follower_profiles"})
    write_json("reports/community_stats.json", stats)
    write_json("reports/action_summary.json", {"recent_actions": action_data[-100:], "counts": {
        "successful_follows": len(successful_follows),
        "successful_unfollows": sum(a.get("action") == "unfollow" and a.get("status") == "success" for a in action_data),
    }})


if __name__ == "__main__":
    main()
