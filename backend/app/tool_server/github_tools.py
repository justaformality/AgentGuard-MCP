import json
from datetime import datetime, timezone
from typing import Any

from app.services.gemini_service import GeminiServiceError, gemini_service
from app.services.github_service import GitHubServiceError, github_service


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_json_input(input_text: str, required_fields: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(input_text)
    except json.JSONDecodeError as exc:
        raise GitHubServiceError("GitHub tools require valid JSON input.") from exc
    missing = [f for f in required_fields if f not in payload or payload[f] in [None, ""]]
    if missing:
        raise GitHubServiceError(f"Missing required GitHub tool fields: {', '.join(missing)}")
    return payload


def read_github_issue(input_text: str) -> dict[str, Any]:
    payload = _parse_json_input(input_text, ["owner", "repo", "issue_number"])
    issue = github_service.read_issue(str(payload["owner"]), str(payload["repo"]), int(payload["issue_number"]))
    labels = [label.get("name", "") for label in issue.get("labels", []) if isinstance(label, dict)]
    return {
        "tool_name": "read_github_issue",
        "status": "success",
        "summary": f"Retrieved GitHub issue #{issue.get('number')}: {issue.get('title')}",
        "data": {
            "number": issue.get("number"), "title": issue.get("title"), "body": issue.get("body"),
            "state": issue.get("state"), "labels": labels, "author": issue.get("user", {}).get("login"),
            "html_url": issue.get("html_url"),
        },
        "created_at": _timestamp(),
    }


def summarize_pull_request(input_text: str) -> dict[str, Any]:
    payload = _parse_json_input(input_text, ["owner", "repo", "pull_number"])
    owner, repo, number = str(payload["owner"]), str(payload["repo"]), int(payload["pull_number"])
    pr = github_service.read_pull_request(owner, repo, number)
    files = github_service.read_pull_request_files(owner, repo, number)
    compact_files = [
        {"filename": f.get("filename"), "status": f.get("status"), "additions": f.get("additions"),
         "deletions": f.get("deletions"), "changes": f.get("changes")}
        for f in files[:100]
    ]
    context = {
        "number": pr.get("number"), "title": pr.get("title"), "body": pr.get("body") or "",
        "author": pr.get("user", {}).get("login"), "base": pr.get("base", {}).get("ref"),
        "head": pr.get("head", {}).get("ref"), "changed_files": pr.get("changed_files"),
        "additions": pr.get("additions"), "deletions": pr.get("deletions"), "files": compact_files,
    }
    prompt = f"""You are a senior code reviewer. Summarize this GitHub pull request for engineers and QA.
Return ONLY JSON with keys: summary (string), key_changes (array), testing_impact (array), risk_level (Low|Medium|High), risk_reasons (array), recommended_checks (array).
PR data:\n{json.dumps(context)}"""
    ai_powered = True
    try:
        analysis = gemini_service.generate_json(prompt)
    except GeminiServiceError as exc:
        ai_powered = False
        hot = any(word in (pr.get("title") or "").lower() + " " + (pr.get("body") or "").lower() for word in ["auth", "security", "payment", "migration", "permission"])
        analysis = {
            "summary": f"PR #{number} changes {len(files)} file(s) with {pr.get('additions', 0)} additions and {pr.get('deletions', 0)} deletions.",
            "key_changes": [f["filename"] for f in compact_files[:8]],
            "testing_impact": ["Run tests covering the changed files and affected user flows."],
            "risk_level": "High" if hot else ("Medium" if len(files) > 10 else "Low"),
            "risk_reasons": ["Deterministic fallback used because Gemini is unavailable.", str(exc)],
            "recommended_checks": ["Review CI status.", "Verify regression coverage.", "Manually test high-impact changed flows."],
        }
    return {
        "tool_name": "summarize_pull_request", "status": "success" if ai_powered else "fallback",
        "summary": analysis.get("summary", f"Summarized PR #{number}."),
        "data": {"pull_request": context, "analysis": analysis, "html_url": pr.get("html_url")},
        "created_at": _timestamp(), "ai_powered": ai_powered,
    }


def create_github_issue(input_text: str) -> dict[str, Any]:
    payload = _parse_json_input(input_text, ["owner", "repo", "title", "body"])
    labels = payload.get("labels", [])
    if not isinstance(labels, list):
        raise GitHubServiceError("'labels' must be a JSON list.")
    issue = github_service.create_issue(
        str(payload["owner"]), str(payload["repo"]), str(payload["title"]), str(payload["body"]),
        [str(label) for label in labels],
    )
    return {
        "tool_name": "create_github_issue", "status": "success",
        "summary": f"Created GitHub issue #{issue.get('number')}: {issue.get('title')}",
        "data": {"number": issue.get("number"), "title": issue.get("title"), "body": issue.get("body"),
                 "state": issue.get("state"), "html_url": issue.get("html_url")},
        "created_at": _timestamp(),
    }