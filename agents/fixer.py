"""Fixer (owner: Dev C). Writes the remediation plan with ASI1 and files a GitHub issue on approval."""
import asyncio
import logging
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from uagents import Agent, Context

from agents.mocks import mock_fix
from agents.models import Finding, FixRequest, FixResult

load_dotenv()
logger = logging.getLogger("fixer")

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

agent = Agent(
    name="dependency-fix-fixer",
    seed=os.environ.get("FIXER_SEED", "dev-only-change-me-fixer"),
    port=8004,
    mailbox=True,
)

# In-memory storage for remediation plan and issue drafts keyed by session_id
DRAFTS: dict[str, dict[str, str]] = {}


def _generate_fallback_plan(findings: list[Finding]) -> tuple[str, str, str]:
    """Generate a clean Markdown remediation plan and issue draft without an external LLM."""
    if not findings:
        plan = "No vulnerable components identified. No remediation action required."
        title = "Security Audit: No vulnerabilities detected"
        body = "All scanned dependencies appear secure based on the latest advisory data."
        return plan, title, body

    plan_lines = ["### Remediation Plan\n"]
    for f in findings:
        fixed = ", ".join(f.fixed_in) if f.fixed_in else "review advisory"
        plan_lines.append(
            f"- **{f.component}** (Severity: {f.severity.upper()}): "
            f"Installed `{f.installed}`, upgrade to `{fixed}`. Advisory: {f.advisory_id}"
        )
    plan_lines.append("\n#### Recommended Steps:")
    plan_lines.append("1. Update the dependency version in your package configuration.")
    plan_lines.append("2. Run tests to confirm backward compatibility.")
    plan_lines.append("3. Deploy updated dependencies to staging and production.")

    plan_markdown = "\n".join(plan_lines)
    if len(findings) == 1:
        title = f"Fix {findings[0].severity.upper()} vulnerability in {findings[0].component} ({findings[0].advisory_id})"
    else:
        title = f"Fix {len(findings)} security vulnerabilities in dependencies"

    body_lines = [
        "## Dependency Fix Crew: Security Remediation\n",
        "The following security advisories affect this project:\n",
        "| Component | Advisory | Severity | Installed | Fixed In |",
        "|---|---|---|---|---|",
    ]
    for f in findings:
        fixed = ", ".join(f.fixed_in) if f.fixed_in else "None"
        body_lines.append(
            f"| `{f.component}` | {f.advisory_id} | {f.severity} | `{f.installed}` | `{fixed}` |"
        )
    body_lines.append("\n### Action Items")
    body_lines.append(plan_markdown)
    if any(f.sources for f in findings):
        body_lines.append("\n### References")
        for f in findings:
            for s in f.sources:
                body_lines.append(f"- {s}")

    issue_body = "\n".join(body_lines)
    return plan_markdown, title, issue_body


def _call_asi1_sync(api_key: str, prompt: str) -> str:
    """Synchronous OpenAI completion call executed in a separate worker thread."""
    client = OpenAI(
        base_url="https://api.asi1.ai/v1",
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )
    completion = client.chat.completions.create(
        model="asi1",
        messages=[
            {"role": "system", "content": "You write clear, actionable security remediation plans and GitHub issues."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content or ""


async def _generate_with_asi1(target: str, findings: list[Finding]) -> tuple[str, str, str]:
    """Generate remediation plan and issue draft with ASI1, falling back to local template on error or timeout."""
    api_key = os.environ.get("ASI1_API_KEY", "").strip()
    if not api_key:
        return _generate_fallback_plan(findings)

    findings_summary = []
    for f in findings:
        fixed = ", ".join(f.fixed_in) if f.fixed_in else "None"
        findings_summary.append(
            f"- Component: {f.component}, Advisory: {f.advisory_id}, Severity: {f.severity}, "
            f"Installed: {f.installed}, Fixed In: {fixed}"
        )
    findings_text = "\n".join(findings_summary) if findings_summary else "No findings."

    prompt = (
        f"You are a software security assistant creating a remediation plan and GitHub issue for target '{target}'.\n"
        f"Findings:\n{findings_text}\n\n"
        "Provide your output formatted with these exact section markers:\n"
        "===PLAN===\n"
        "<concise remediation steps for the user>\n"
        "===TITLE===\n"
        "<a clear GitHub issue title>\n"
        "===BODY===\n"
        "<detailed GitHub issue body in markdown>\n"
    )

    try:
        content = await asyncio.to_thread(_call_asi1_sync, api_key, prompt)
        if "===PLAN===" in content and "===TITLE===" in content and "===BODY===" in content:
            plan_part = content.split("===PLAN===")[1].split("===TITLE===")[0].strip()
            title_part = content.split("===TITLE===")[1].split("===BODY===")[0].strip()
            body_part = content.split("===BODY===")[1].strip()
            if plan_part and title_part and body_part:
                return plan_part, title_part, body_part
        elif content.strip():
            _, fallback_title, fallback_body = _generate_fallback_plan(findings)
            return content.strip(), fallback_title, f"{content.strip()}\n\n{fallback_body}"
    except (OpenAIError, requests.RequestException, ValueError, TimeoutError) as err:
        logger.warning("ASI1 generation failed or timed out, falling back to local template: %s", err)

    return _generate_fallback_plan(findings)


def _parse_github_repo(target: str) -> str | None:
    """Parse 'owner/repo' from a repository slug or URL, with DEMO_REPO as fallback."""
    t = (target or "").strip()

    if "github.com" in t:
        after = t.split("github.com", 1)[1].lstrip(":/")
        parts = [p for p in after.strip("/").split("/") if p]
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].removesuffix(".git")
            if owner and repo:
                return f"{owner}/{repo}"

    if "/" in t and not t.startswith("http://") and not t.startswith("https://"):
        parts = [p.strip() for p in t.strip("/").split("/")]
        if len(parts) == 2 and parts[0] and parts[1]:
            repo = parts[1].removesuffix(".git")
            return f"{parts[0]}/{repo}"

    demo = os.environ.get("DEMO_REPO", "").strip()
    if demo:
        if "github.com" in demo:
            after = demo.split("github.com", 1)[1].lstrip(":/")
            parts = [p for p in after.strip("/").split("/") if p]
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1].removesuffix('.git')}"
        elif "/" in demo:
            parts = [p.strip() for p in demo.strip("/").split("/")]
            if len(parts) == 2 and parts[0] and parts[1]:
                return f"{parts[0]}/{parts[1].removesuffix('.git')}"

    return None


def _create_github_issue(repo: str, title: str, body: str) -> tuple[bool, str, str]:
    """Create a GitHub issue using GITHUB_TOKEN and return (ok, issue_url, error)."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        return False, "", "GITHUB_TOKEN is missing or not configured in environment"

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "dependency-fix-crew",
    }
    payload = {"title": title, "body": body}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 201:
            data = resp.json()
            issue_url = data.get("html_url", "")
            return True, issue_url, ""
        error_msg = f"GitHub API error ({resp.status_code}): {resp.text}"
        try:
            data = resp.json()
            if "message" in data:
                error_msg = f"GitHub API error ({resp.status_code}): {data['message']}"
        except ValueError:
            logger.debug("GitHub response was not JSON: %s", resp.text)
        return False, "", error_msg
    except requests.RequestException as e:
        return False, "", f"GitHub API request failed: {e}"


@agent.on_message(FixRequest)
async def on_fix(ctx: Context, sender: str, msg: FixRequest):
    if os.environ.get("USE_MOCKS") == "1":
        await ctx.send(sender, mock_fix(msg))
        return

    if not msg.file_issue:
        # Phase 1: generate remediation plan & issue draft, store by session_id
        plan_markdown, issue_title, issue_body = await _generate_with_asi1(msg.target, msg.findings)
        DRAFTS[msg.session_id] = {
            "plan_markdown": plan_markdown,
            "issue_title": issue_title,
            "issue_body": issue_body,
        }
        await ctx.send(
            sender,
            FixResult(
                session_id=msg.session_id,
                ok=True,
                plan_markdown=plan_markdown,
                issue_url="",
            ),
        )
        return

    # Phase 2: user approved filing issue
    draft = DRAFTS.get(msg.session_id)
    if not draft:
        await ctx.send(
            sender,
            FixResult(
                session_id=msg.session_id,
                ok=False,
                error=f"No issue draft found for session '{msg.session_id}'. Generate plan first.",
            ),
        )
        return

    repo = _parse_github_repo(msg.target)
    if not repo:
        await ctx.send(
            sender,
            FixResult(
                session_id=msg.session_id,
                ok=False,
                error=f"Invalid target repository: '{msg.target}'. Expected 'owner/repo' or GitHub URL.",
            ),
        )
        return

    ok, issue_url, error = _create_github_issue(
        repo=repo,
        title=draft["issue_title"],
        body=draft["issue_body"],
    )
    if ok:
        await ctx.send(
            sender,
            FixResult(
                session_id=msg.session_id,
                ok=True,
                plan_markdown=draft["plan_markdown"],
                issue_url=issue_url,
            ),
        )
    else:
        await ctx.send(
            sender,
            FixResult(
                session_id=msg.session_id,
                ok=False,
                plan_markdown=draft["plan_markdown"],
                error=error,
            ),
        )


if __name__ == "__main__":
    agent.run()
