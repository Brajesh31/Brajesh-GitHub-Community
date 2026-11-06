import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

from community import eligible_unfollow, execute_mutations, relationship_data
from config import Settings, load_names
from github_api import GitHubApiError, GitHubClient
from get_random_users import merge_candidates


def test_conservative_configuration_defaults(monkeypatch):
    for key in ("AUTO_FOLLOW_ENABLED", "AUTO_FOLLOW_BACK_ENABLED", "AUTO_UNFOLLOW_ENABLED", "DRY_RUN"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.from_environment(token="secret")
    assert settings.username == "Brajesh31"
    assert not settings.auto_follow_enabled
    assert not settings.auto_follow_back_enabled
    assert not settings.auto_unfollow_enabled
    assert settings.dry_run


def test_pagination_and_empty_response():
    client = GitHubClient("secret", max_retries=0)
    client.request = Mock(side_effect=[
        Mock(ok=True, json=lambda: [{"login": "one"}] * 100),
        Mock(ok=True, json=lambda: [{"login": "two"}]),
    ])
    assert [u["login"] for u in client.paged("/users")] == ["one"] * 100 + ["two"]


def test_relationship_deduplicates():
    client = Mock()
    client.users.side_effect = [
        [{"login": "a"}, {"login": "a"}, {"login": "b"}],
        [{"login": "b"}, {"login": "c"}],
    ]
    data = relationship_data(client, "Brajesh31")
    assert data["followers"] == ["a", "b"]
    assert data["mutual"] == ["b"]
    assert data["following_not_following_back"] == ["c"]


def test_candidate_discovery_filters_and_deduplicates():
    users = [{"login": "Brajesh31"}, {"login": "blocked"}, {"login": "new"}, {"login": "new"}]
    candidates = merge_candidates(users, [], "Brajesh31", {"following"}, {"blocked"}, {"completed"})
    assert [item["username"] for item in candidates] == ["new"]


def test_whitelist_blacklist_and_wait(tmp_path):
    follow_history = tmp_path / "follow_history.json"
    follow_history.write_text(json.dumps([{
        "username": "old", "date_followed": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    }]))
    (tmp_path / "whitelist.txt").write_text("protected\n")
    (tmp_path / "blacklist.txt").write_text("blocked\n")
    assert "protected" in load_names(str(tmp_path / "whitelist.txt"))
    assert eligible_unfollow(str(tmp_path), "old", 14, {"protected"}, {"blocked"})
    assert not eligible_unfollow(str(tmp_path), "protected", 14, {"protected"}, set())
    assert not eligible_unfollow(str(tmp_path), "new", 14, set(), set())


def test_dry_run_does_not_call_mutation(tmp_path):
    client = Mock()
    client.mutation_permissions.return_value = True
    settings = Settings(token="secret", data_dir=str(tmp_path), dry_run=True)
    result = execute_mutations(client, ["candidate"], "follow", settings, "discovery")
    client.follow.assert_not_called()
    assert result[0]["status"] == "dry_run"


def test_api_errors_are_bounded():
    client = GitHubClient("secret", max_retries=0)
    response = Mock(ok=False, status_code=422, text="invalid", headers={})
    client.session.request = Mock(return_value=response)
    with pytest.raises(GitHubApiError) as error:
        client.request("PUT", "/user/following/test")
    assert error.value.status_code == 422


def test_bearer_authentication_header():
    client = GitHubClient("secret")
    assert client.session.headers["Authorization"] == "Bearer secret"


def test_report_generation_preserves_documentation(tmp_path, monkeypatch):
    import create_readme

    class FakeClient:
        def require_identity(self, username):
            return {"login": username}

        def users(self, relationship, username):
            return [{"login": "follower", "avatar_url": "avatar"}] if relationship == "followers" else []

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(create_readme, "GitHubClient", lambda token: FakeClient())
    (tmp_path / "README.md").write_text("# Documentation\n\nKeep this section.\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["create_readme.py"])
    monkeypatch.setenv("MY_FOLLOWERS", "secret")
    create_readme.main()
    report = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Keep this section." in report
    assert "COMMUNITY_REPORT_START" in report
    assert json.loads((tmp_path / "reports" / "community_stats.json").read_text())["followers"] == 1
