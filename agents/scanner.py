
"""Scanner (owner: Dev B). Reads PHP version information and Composer packages."""

import base64
import json
import os
import re

import requests
from dotenv import load_dotenv
from uagents import Agent, Context

from agents.mocks import mock_scan
from agents.models import ScanRequest, ScanResult

load_dotenv()


def fetch_github_file(owner: str, repo: str, path: str) -> dict:
    """Fetch a file from GitHub with a timeout and one retry."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json"}

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if attempt == 1:
                raise

    raise RuntimeError("GitHub request failed.")


def read_github_text(owner: str, repo: str, path: str) -> str:
    """Read and decode a text file from GitHub."""
    data = fetch_github_file(owner, repo, path)
    content = data.get("content")

    if not content:
        raise ValueError(f"GitHub returned no content for {path}.")

    return base64.b64decode(content).decode("utf-8")


def read_optional_file(owner: str, repo: str, path: str):
    """Return None when an optional file does not exist."""
    try:
        return read_github_text(owner, repo, path)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def exact_php_version(value: str):
    """Return a full numeric PHP version, never a partial version."""
    match = re.fullmatch(r"\s*v?(\d+\.\d+\.\d+)\s*", value)
    return match.group(1) if match else None


def detect_php_version(owner: str, repo: str, composer_json: dict):
    """Return (exact version, constraint, source)."""

    # 1. Look for a pinned runtime version.
    dockerfile = read_optional_file(owner, repo, "Dockerfile")
    if dockerfile:
        for line in dockerfile.splitlines():
            match = re.match(
                r"^\s*FROM\s+(?:--platform=\S+\s+)?(?:\S*/)?php:(\d+\.\d+\.\d+)(?:[-@\s]|$)",
                line,
                re.IGNORECASE,
            )
            if match:
                return match.group(1), "", "Dockerfile"

    php_version_file = read_optional_file(owner, repo, ".php-version")
    if php_version_file:
        version = exact_php_version(php_version_file)
        if version:
            return version, "", ".php-version"

    tool_versions = read_optional_file(owner, repo, ".tool-versions")
    if tool_versions:
        for line in tool_versions.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "php":
                version = exact_php_version(parts[1])
                if version:
                    return version, "", ".tool-versions"

    # 2. Check Composer's explicit platform PHP pin.
    platform_php = (
        composer_json.get("config", {})
        .get("platform", {})
        .get("php", "")
    )
    if isinstance(platform_php, str):
        version = exact_php_version(platform_php)
        if version:
            return version, "", "composer.json config.platform.php"

    # 3. A requirement is a constraint, not the deployed runtime version.
    require_php = composer_json.get("require", {}).get("php", "")
    if isinstance(require_php, str) and require_php.strip():
        return "", require_php.strip(), "constraint only"

    return "", "", "not found"


agent = Agent(
    name="dependency-fix-scanner",
    seed=os.environ.get("SCANNER_SEED", "dev-only-change-me-scanner"),
    port=8002,
    mailbox=True,
)


@agent.on_message(ScanRequest)
async def on_scan(ctx: Context, sender: str, msg: ScanRequest):
    if os.environ.get("USE_MOCKS") == "1":
        await ctx.send(sender, mock_scan(msg))
        return

    if msg.kind == "version":
        await ctx.send(
            sender,
            ScanResult(
                session_id=msg.session_id,
                ok=True,
                php_version=msg.target,
                version_source="user input",
                source="user-provided version",
            ),
        )
        return

    if msg.kind != "repo":
        await ctx.send(
            sender,
            ScanResult(
                session_id=msg.session_id,
                ok=False,
                error=f"Unsupported scan kind: {msg.kind}",
            ),
        )
        return

    try:
        parts = msg.target.strip("/").split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("Repository target must use owner/name format.")

        owner, repo = parts

        composer_json = json.loads(
            read_github_text(owner, repo, "composer.json")
        )
        composer_lock = json.loads(
            read_github_text(owner, repo, "composer.lock")
        )

        if not isinstance(composer_json, dict):
            raise ValueError("composer.json must contain a JSON object.")
        if not isinstance(composer_lock, dict):
            raise ValueError("composer.lock must contain a JSON object.")

        php_version, php_constraint, version_source = detect_php_version(
            owner, repo, composer_json
        )

        packages = {}
        for package in (
            composer_lock.get("packages", [])
            + composer_lock.get("packages-dev", [])
        ):
            if not isinstance(package, dict):
                continue

            name = package.get("name")
            version = package.get("version")
            if name and version:
                packages[name] = version

        await ctx.send(
            sender,
            ScanResult(
                session_id=msg.session_id,
                ok=True,
                php_version=php_version,
                php_constraint=php_constraint,
                version_source=version_source,
                packages=packages,
                source=f"GitHub repository: {owner}/{repo}",
            ),
        )

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        await ctx.send(
            sender,
            ScanResult(
                session_id=msg.session_id,
                ok=False,
                error=f"Repository scan failed: {exc}",
            ),
        )


if __name__ == "__main__":
    agent.run()
