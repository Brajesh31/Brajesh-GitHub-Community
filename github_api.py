"""Small, resilient GitHub REST API client used by the project scripts."""

from typing import Dict, Iterator, List, Optional

import requests


API_URL = "https://api.github.com"
TIMEOUT_SECONDS = 30


class GitHubApiError(RuntimeError):
    """Raised when GitHub returns an unsuccessful response."""


class GitHubClient:
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Brajesh-GitHub-Community",
            }
        )

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        response = self.session.request(
            method, f"{API_URL}{path}", timeout=TIMEOUT_SECONDS, **kwargs
        )
        if not response.ok:
            detail = response.text[:300].replace("\n", " ")
            raise GitHubApiError(
                f"GitHub API {response.status_code} for {path}: {detail}"
            )
        return response

    def verify_token(self) -> Dict[str, str]:
        return self.request("GET", "/user").json()

    def paged(
        self, path: str, params: Optional[dict] = None, max_pages: Optional[int] = None
    ) -> Iterator[dict]:
        page = 1
        while True:
            if max_pages is not None and page > max_pages:
                return
            query = dict(params or {})
            query.update({"per_page": 100, "page": page})
            items = self.request("GET", path, params=query).json()
            if not isinstance(items, list):
                raise GitHubApiError(f"Expected a list response from {path}")
            yield from items
            if len(items) < 100:
                return
            page += 1

    def users(self, relationship: str, username: str) -> List[dict]:
        return list(self.paged(f"/users/{username}/{relationship}"))

    def follow(self, username: str) -> None:
        self.request("PUT", f"/user/following/{username}")

    def unfollow(self, username: str) -> None:
        self.request("DELETE", f"/user/following/{username}")
