"""Centralized, conservative configuration for community automation."""

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_USERNAME = "Brajesh31"


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return max(0, int(os.getenv(name, str(default))))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    username: str = DEFAULT_USERNAME
    token: str = ""
    auto_discovery_enabled: bool = True
    auto_follow_enabled: bool = True
    auto_follow_back_enabled: bool = True
    auto_unfollow_enabled: bool = True
    dry_run: bool = False
    max_follow_actions: int = 5
    max_unfollow_actions: int = 5
    max_follow_actions_per_day: int = 20
    max_unfollow_actions_per_day: int = 20
    min_unfollow_wait_days: int = 14
    whitelist_path: str = "whitelist.txt"
    blacklist_path: str = "blacklist.txt"
    log_level: str = "INFO"
    data_dir: str = "data"

    @classmethod
    def from_environment(cls, username: str | None = None, token: str | None = None):
        return cls(
            username=username or os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME),
            token=token or os.getenv("MY_FOLLOWERS") or os.getenv("GITHUB_TOKEN", ""),
            auto_discovery_enabled=_bool("AUTO_DISCOVERY_ENABLED", True),
            auto_follow_enabled=_bool("AUTO_FOLLOW_ENABLED", True),
            auto_follow_back_enabled=_bool("AUTO_FOLLOW_BACK_ENABLED", True),
            auto_unfollow_enabled=_bool("AUTO_UNFOLLOW_ENABLED", True),
            dry_run=_bool("DRY_RUN", False),
            max_follow_actions=_int("MAX_FOLLOW_ACTIONS", 5),
            max_unfollow_actions=_int("MAX_UNFOLLOW_ACTIONS", 5),
            max_follow_actions_per_day=_int("MAX_FOLLOW_ACTIONS_PER_DAY", 20),
            max_unfollow_actions_per_day=_int("MAX_UNFOLLOW_ACTIONS_PER_DAY", 20),
            min_unfollow_wait_days=_int("MIN_UNFOLLOW_WAIT_DAYS", 14),
            whitelist_path=os.getenv("WHITELIST_PATH", "whitelist.txt"),
            blacklist_path=os.getenv("BLACKLIST_PATH", "blacklist.txt"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            data_dir=os.getenv("DATA_DIR", "data"),
        )

    def configure_logging(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self.log_level, logging.INFO),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    def require_token(self) -> None:
        if not self.token:
            raise SystemExit("Set MY_FOLLOWERS (or pass --token) before running.")


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-m", "--username", default=None)
    parser.add_argument("-t", "--token", default=None)
    parser.add_argument("--allow-mutations", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="Force simulation mode.")


def settings_from_args(args: argparse.Namespace) -> Settings:
    settings = Settings.from_environment(args.username, args.token)
    if getattr(args, "allow_mutations", False):
        settings = Settings(**{**settings.__dict__, "auto_follow_enabled": True,
                               "auto_follow_back_enabled": True,
                               "auto_unfollow_enabled": True, "dry_run": False})
    if getattr(args, "dry_run", False):
        settings = Settings(**{**settings.__dict__, "dry_run": True})
    settings.require_token()
    return settings


def load_names(path: str) -> set[str]:
    try:
        return {
            line.strip().lower()
            for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
    except FileNotFoundError:
        return set()
