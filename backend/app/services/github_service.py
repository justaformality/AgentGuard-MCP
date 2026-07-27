from typing import Any

import requests

from app.config import settings


class GitHubServiceError(Exception):
    """Raised when a GitHub API request cannot be completed safely."""


class GitHubService:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self):
        self.token = settings.github_token

    def _headers(
        self,
        require_auth: bool = False,
    ) -> dict[str, str]:

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION,
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        elif require_auth:
            raise GitHubServiceError(
                "GITHUB_TOKEN is missing. "
                "Add a fine-grained GitHub token to backend/.env "
                "before using GitHub write actions."
            )

        return headers

    @staticmethod
    def _handle_response(
        response: requests.Response,
    ) -> Any:

        try:
            data = response.json()

        except ValueError:
            data = {
                "message":
                    response.text[:500]
                    or "GitHub returned an empty response."
            }

        if response.ok:
            return data

        message = (
            data.get(
                "message",
                "Unknown GitHub API error.",
            )
            if isinstance(data, dict)
            else str(data)
        )

        raise GitHubServiceError(
            "GitHub API request failed "
            f"with status {response.status_code}: {message}"
        )

    def _get(
        self,
        path: str,
    ) -> Any:

        try:
            response = requests.get(
                f"{self.BASE_URL}{path}",
                headers=self._headers(
                    require_auth=False
                ),
                timeout=15,
            )

        except requests.RequestException as exc:
            raise GitHubServiceError(
                f"Could not connect to GitHub: {exc}"
            ) from exc

        return self._handle_response(response)

    def read_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> dict[str, Any]:

        return self._get(
            f"/repos/{owner}/{repo}"
            f"/issues/{issue_number}"
        )

    def read_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict[str, Any]:

        return self._get(
            f"/repos/{owner}/{repo}"
            f"/pulls/{pull_number}"
        )

    def read_pull_request_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> list[dict[str, Any]]:

        result = self._get(
            f"/repos/{owner}/{repo}"
            f"/pulls/{pull_number}/files"
            "?per_page=100"
        )

        if not isinstance(result, list):
            raise GitHubServiceError(
                "GitHub returned an unexpected "
                "PR files response."
            )

        return result

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repo}/issues"
        )

        payload: dict[str, Any] = {
            "title": title,
            "body": body,
        }

        if labels:
            payload["labels"] = labels

        try:
            response = requests.post(
                url,
                headers=self._headers(
                    require_auth=True
                ),
                json=payload,
                timeout=15,
            )

        except requests.RequestException as exc:
            raise GitHubServiceError(
                "Could not connect to GitHub "
                f"while creating the issue: {exc}"
            ) from exc

        return self._handle_response(response)


github_service = GitHubService()