"""Shared relationship and report helpers."""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Sequence

from github_api import GitHubClient


LOGGER = logging.getLogger(__name__)


def unique_logins(users: Iterable[dict]) -> List[str]:
    return sorted({user["login"] for user in users if user.get("login")})


def relationship_data(client: GitHubClient, username: str) -> dict:
    followers = client.users("followers", username)
    following = client.users("following", username)
    follower_names = set(unique_logins(followers))
    following_names = set(unique_logins(following))
    return {
        "followers": sorted(follower_names),
        "following": sorted(following_names),
        "mutual": sorted(follower_names & following_names),
        "followers_not_followed": sorted(follower_names - following_names),
        "following_not_following_back": sorted(following_names - follower_names),
        "follower_profiles": sorted(
            {
                (user["login"], user.get("avatar_url", ""))
                for user in followers
                if user.get("login")
            }
        ),
    }


def atomic_write(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=destination.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = handle.name
    os.replace(temporary, destination)


def write_json(path: str, value) -> None:
    atomic_write(path, json.dumps(value, indent=2) + "\n")


def write_lines(path: str, values: Sequence[str]) -> None:
    atomic_write(path, "".join(f"{value}\n" for value in sorted(set(values))))


def mutation_report(action: str, candidates: Sequence[str], client: GitHubClient, enabled: bool) -> None:
    if not enabled:
        LOGGER.info(
            "%s is disabled by default; %d candidates were reported only.",
            action,
            len(candidates),
        )
        return
    for username in candidates:
        try:
            getattr(client, action)(username)
            LOGGER.info("%s %s", action, username)
        except Exception:
            LOGGER.exception("Unable to %s %s", action, username)
