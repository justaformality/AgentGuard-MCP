import json

import pytest

from app.services.github_service import GitHubServiceError
from app.tool_server import github_tools
from app.tool_server.github_tools import (
    create_github_issue,
    read_github_issue,
)


def test_read_github_issue_returns_structured_result(monkeypatch):
    def fake_read_issue(owner, repo, issue_number):
        assert owner == "demo-user"
        assert repo == "demo-repo"
        assert issue_number == 1

        return {
            "number": 1,
            "title": "Password reset bug",
            "body": "Expired token causes an unclear error.",
            "state": "open",
            "labels": [{"name": "bug"}],
            "user": {"login": "demo-user"},
            "html_url": "https://github.com/demo-user/demo-repo/issues/1",
        }

    monkeypatch.setattr(
        github_tools.github_service,
        "read_issue",
        fake_read_issue,
    )

    result = read_github_issue(
        json.dumps(
            {
                "owner": "demo-user",
                "repo": "demo-repo",
                "issue_number": 1,
            }
        )
    )

    assert result["tool_name"] == "read_github_issue"
    assert result["status"] == "success"
    assert result["data"]["title"] == "Password reset bug"
    assert result["data"]["labels"] == ["bug"]


def test_create_github_issue_returns_structured_result(monkeypatch):
    def fake_create_issue(owner, repo, title, body, labels=None):
        assert owner == "demo-user"
        assert repo == "demo-repo"
        assert title == "Missing test coverage"
        assert labels == ["bug"]

        return {
            "number": 2,
            "title": title,
            "body": body,
            "state": "open",
            "html_url": "https://github.com/demo-user/demo-repo/issues/2",
        }

    monkeypatch.setattr(
        github_tools.github_service,
        "create_issue",
        fake_create_issue,
    )

    result = create_github_issue(
        json.dumps(
            {
                "owner": "demo-user",
                "repo": "demo-repo",
                "title": "Missing test coverage",
                "body": "Add expired token tests.",
                "labels": ["bug"],
            }
        )
    )

    assert result["tool_name"] == "create_github_issue"
    assert result["status"] == "success"
    assert result["data"]["number"] == 2


def test_github_tool_rejects_invalid_json():
    with pytest.raises(GitHubServiceError):
        read_github_issue("this is not JSON")


def test_github_tool_rejects_missing_fields():
    with pytest.raises(GitHubServiceError):
        create_github_issue(
            json.dumps(
                {
                    "owner": "demo-user",
                    "repo": "demo-repo",
                }
            )
        )