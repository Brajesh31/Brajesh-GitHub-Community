"""Resilient GitHub REST API client with bounded retries and safe logging."""

import time
from typing import Dict, Iterator, List, Optional

import requests

API_URL = "https://api.github.com"
TIMEOUT_SECONDS = 30
TRANSIENT_STATUS_CODES = {500, 502, 503, 504}


class GitHubApiError(RuntimeError):
    def __init__(self, status_code: int, path: str, message: str):
        super().__init__(f"GitHub API {status_code} for {path}: {message}")
        self.status_code = status_code
        self.path = path


class GitHubClient:
    def __init__(self, token: str, max_retries: int = 3, session=None):
        self.session = session or requests.Session()
        self.max_retries = max(0, max_retries)
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Brajesh-GitHub-Community",
            }
        )

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, f"{API_URL}{path}", timeout=TIMEOUT_SECONDS, **kwargs
                )
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise GitHubApiError(0, path, "network request failed") from exc
                time.sleep(2**attempt)
                continue
            if response.ok:
                return response
            if response.status_code in {401, 403, 429}:
                retry_after = response.headers.get("Retry-After")
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset")
                if response.status_code == 403 and remaining == "0":
                    retry_after = retry_after or (
                        max(0, int(reset or time.time()) - int(time.time()))
                    )
                if retry_after and attempt < self.max_retries:
                    time.sleep(min(60, max(1, int(float(retry_after)))))
                    continue
            if response.status_code in TRANSIENT_STATUS_CODES and attempt < self.max_retries:
                time.sleep(2**attempt)
                continue
            detail = response.text[:300].replace("\n", " ")
            raise GitHubApiError(response.status_code, path, detail)
        raise GitHubApiError(0, path, "retry limit exceeded")

    def verify_token(self) -> Dict[str, str]:
        return self.request("GET", "/user").json()

    def require_identity(self, username: str) -> Dict[str, str]:
        identity = self.verify_token()
        if identity.get("login", "").lower() != username.lower():
            raise GitHubApiError(401, "/user", "token identity does not match configured username")
        return identity

    def paged(self, path: str, params: Optional[dict] = None, max_pages: Optional[int] = None) -> Iterator[dict]:
        page = 1
        while max_pages is None or page <= max_pages:
            query = {**(params or {}), "per_page": 100, "page": page}
            items = self.request("GET", path, params=query).json()
            if not isinstance(items, list):
                raise GitHubApiError(200, path, "expected a list response")
            if not items:
                return
            yield from items
            if len(items) < 100:
                return
            page += 1

    def users(self, relationship: str, username: str) -> List[dict]:
        return list(self.paged(f"/users/{username}/{relationship}"))

    def public_users(self, max_pages: int = 10) -> List[dict]:
        return list(self.paged("/users", max_pages=max_pages))

    def is_following(self, username: str) -> bool:
        response = self.session.get(
            f"{API_URL}/user/following/{username}", timeout=TIMEOUT_SECONDS
        )
        if response.status_code == 204:
            return True
        if response.status_code == 404:
            return False
        if not response.ok:
            raise GitHubApiError(response.status_code, f"/user/following/{username}", response.text[:300])
        return True

    def follow(self, username: str) -> bool:
        return self.request("PUT", f"/user/following/{username}").status_code == 204

    def unfollow(self, username: str) -> bool:
        return self.request("DELETE", f"/user/following/{username}").status_code == 204

    def mutation_permissions(self) -> bool:
        response = self.request("GET", "/user")
        scopes = response.headers.get("X-OAuth-Scopes", "")
        if not scopes.strip():
            # Fine-grained tokens commonly omit X-OAuth-Scopes; the mutation
            # response remains the authoritative permission check.
            return True
        return any(scope.strip() in {"user", "write:user"} for scope in scopes.split(","))
