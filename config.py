"""Shared configuration for the GitHub community analytics tools."""

import argparse
import os
from dataclasses import dataclass


DEFAULT_USERNAME = "Brajesh31"


@dataclass(frozen=True)
class Settings:
    username: str
    token: str
    allow_mutations: bool = False


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-m",
        "--username",
        default=os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME),
        help="GitHub account to inspect (default: GITHUB_USERNAME or Brajesh31).",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=os.getenv("MY_FOLLOWERS") or os.getenv("GITHUB_TOKEN"),
        help="GitHub token; prefer MY_FOLLOWERS locally and Actions.",
    )
    parser.add_argument(
        "--allow-mutations",
        action="store_true",
        help="Explicitly allow follow/unfollow API requests (disabled by default).",
    )


def settings_from_args(args: argparse.Namespace) -> Settings:
    if not args.token:
        raise SystemExit(
            "A GitHub token is required. Set MY_FOLLOWERS or pass --token."
        )
    return Settings(args.username, args.token, args.allow_mutations)
