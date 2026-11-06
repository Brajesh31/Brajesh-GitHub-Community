"""Shared relationship, persistence, history, and mutation helpers."""

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from config import load_names
from github_api import GitHubApiError, GitHubClient

LOGGER = logging.getLogger(__name__)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def unique_logins(users: Iterable[dict]) -> list[str]:
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
            {(u["login"], u.get("avatar_url", "")) for u in followers if u.get("login")}
        ),
    }


def atomic_write(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent, delete=False) as handle:
        handle.write(content)
        temporary = handle.name
    os.replace(temporary, destination)


def read_json(path: str, default):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: str, value) -> None:
    atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_lines(path: str, values: Sequence[str]) -> None:
    atomic_write(path, "".join(f"{value}\n" for value in sorted(set(values))))


def paths(data_dir: str) -> dict[str, str]:
    return {name: str(Path(data_dir) / name) for name in (
        "follow_history.json", "unfollow_history.json", "candidates.json", "action_history.json"
    )}


def history(path: str) -> list[dict]:
    value = read_json(path, [])
    return value if isinstance(value, list) else []


def record_action(data_dir: str, username: str, action: str, source: str, status: str, error: str = "") -> dict:
    files = paths(data_dir)
    entry = {"username": username, "action": action, "source": source, "status": status, "timestamp": now()}
    actions = history(files["action_history.json"])
    actions.append({**entry, **({"error": error} if error else {})})
    write_json(files["action_history.json"], actions)
    if action == "follow" and status == "success":
        follows = history(files["follow_history.json"])
        follows.append({"username": username, "date_followed": entry["timestamp"], "source": source, "status": status})
        write_json(files["follow_history.json"], follows)
    if action == "unfollow" and status == "success":
        unfollows = history(files["unfollow_history.json"])
        unfollows.append({"username": username, "date_unfollowed": entry["timestamp"], "source": source, "status": status})
        write_json(files["unfollow_history.json"], unfollows)
    return entry


def followed_history(data_dir: str) -> set[str]:
    follows = {}
    for item in history(paths(data_dir)["follow_history.json"]):
        if item.get("username") and item.get("date_followed"):
            follows[item["username"].lower()] = item["date_followed"]
    unfollows = {}
    for item in history(paths(data_dir)["unfollow_history.json"]):
        if item.get("username") and item.get("date_unfollowed"):
            unfollows[item["username"].lower()] = item["date_unfollowed"]
    return {
        username for username, followed_at in follows.items()
        if followed_at > unfollows.get(username, "")
    }


def eligible_unfollow(data_dir: str, username: str, wait_days: int, whitelist: set[str], blacklist: set[str]) -> bool:
    if username.lower() in whitelist or username.lower() in blacklist:
        return False
    latest_follow = None
    for item in reversed(history(paths(data_dir)["follow_history.json"])):
        if item.get("username", "").lower() == username.lower() and item.get("date_followed"):
            latest_follow = item["date_followed"]
            break
    if latest_follow is None:
        return False
    for item in reversed(history(paths(data_dir)["unfollow_history.json"])):
        if (
            item.get("username", "").lower() == username.lower()
            and item.get("date_unfollowed", "") >= latest_follow
        ):
            return False
    followed = datetime.fromisoformat(latest_follow)
    return (datetime.now(timezone.utc) - followed).days >= wait_days


def execute_mutations(client: GitHubClient, candidates: Sequence[str], action: str, settings, source: str) -> list[dict]:
    whitelist = load_names(settings.whitelist_path)
    blacklist = load_names(settings.blacklist_path)
    existing = followed_history(settings.data_dir)
    today = now()[:10]
    action_name = action
    actions_today = sum(
        item.get("action") == action_name
        and item.get("status") == "success"
        and item.get("timestamp", "").startswith(today)
        for item in history(paths(settings.data_dir)["action_history.json"])
    )
    daily_limit = (
        settings.max_follow_actions_per_day
        if action == "follow"
        else settings.max_unfollow_actions_per_day
    )
    execution_limit = (
        settings.max_follow_actions
        if action == "follow"
        else settings.max_unfollow_actions
    )
    remaining_daily = max(0, daily_limit - actions_today)
    eligible = [
        name for name in candidates
        if name.lower() != settings.username.lower()
        and name.lower() not in blacklist
        and (action != "follow" or name.lower() not in existing)
    ][:min(execution_limit, remaining_daily)]
    results = []
    if not getattr(settings, f"auto_{'follow_back' if source == 'follow-back' else action}_enabled", False) or settings.dry_run:
        LOGGER.info("Dry-run or disabled: %s %d candidates", action, len(eligible))
        return [record_action(settings.data_dir, name, action, source, "dry_run") for name in eligible]
    if not client.mutation_permissions():
        raise GitHubApiError(403, "/user", "token lacks mutation permission")
    for name in eligible:
        if action == "unfollow" and not eligible_unfollow(settings.data_dir, name, settings.min_unfollow_wait_days, whitelist, blacklist):
            continue
        try:
            success = getattr(client, action)(name)
            results.append(record_action(settings.data_dir, name, action, source, "success" if success else "failed"))
        except GitHubApiError as exc:
            results.append(record_action(settings.data_dir, name, action, source, "failed", str(exc)))
            if exc.status_code in {403, 429}:
                break
    return results
