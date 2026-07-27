import json
from app.tool_server import github_tools
from app.tool_server.github_tools import summarize_pull_request


def test_summarize_pull_request_fallback(monkeypatch):
    monkeypatch.setattr(github_tools.github_service, "read_pull_request", lambda owner, repo, n: {
        "number": n, "title": "Add auth checks", "body": "Improve permission validation", "user": {"login": "dev"},
        "base": {"ref": "main"}, "head": {"ref": "auth"}, "changed_files": 1, "additions": 10, "deletions": 2,
        "html_url": "https://github.com/org/repo/pull/7",
    })
    monkeypatch.setattr(github_tools.github_service, "read_pull_request_files", lambda owner, repo, n: [
        {"filename": "auth.py", "status": "modified", "additions": 10, "deletions": 2, "changes": 12}
    ])
    def no_ai(prompt):
        from app.services.gemini_service import GeminiServiceError
        raise GeminiServiceError("no key")
    monkeypatch.setattr(github_tools.gemini_service, "generate_json", no_ai)
    result = summarize_pull_request(json.dumps({"owner":"org","repo":"repo","pull_number":7}))
    assert result["tool_name"] == "summarize_pull_request"
    assert result["status"] == "fallback"
    assert result["data"]["analysis"]["risk_level"] == "High"