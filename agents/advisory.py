
"""Advisory Researcher (owner: Dev B). Matches PHP and Composer advisories."""

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv
from uagents import Agent, Context

from agents.mocks import mock_advisory
from agents.models import AdvisoryRequest, AdvisoryResult, Finding

load_dotenv()

ADVISORIES_FILE = Path(__file__).resolve().parent.parent / "data" / "advisories.json"
OSV_URL = "https://api.osv.dev/v1/query"


def load_advisories() -> list:
    with ADVISORIES_FILE.open(encoding="utf-8") as file:
        data = json.load(file)
    advisories = data.get("advisories")
    if not isinstance(advisories, list):
        raise ValueError("Invalid advisories.json: expected an advisories list.")
    return advisories


def version_tuple(version: str):
    match = re.fullmatch(r"\s*v?(\d+)\.(\d+)\.(\d+)\s*", version)
    if not match:
        raise ValueError(f"Cannot compare non-exact PHP version: {version}")
    return tuple(map(int, match.groups()))


def check_php_version(version: str, advisories: list) -> list:
    installed = version_tuple(version)
    findings = []

    for advisory in advisories:
        fixed_versions = advisory.get("fixed_in", [])
        same_branch_fixes = [
            version_tuple(fixed)
            for fixed in fixed_versions
            if version_tuple(fixed)[:2] == installed[:2]
        ]

        if same_branch_fixes:
            affected = installed < min(same_branch_fixes)
        else:
            # The advisory's data says branches below 8.2 are EOL.
            affected = installed[:2] < (8, 2)

        findings.append(
            Finding(
                advisory_id=advisory["id"],
                component=advisory.get("component", "php-core"),
                severity=advisory.get("severity", "unknown"),
                affected=affected,
                installed=version,
                fixed_in=fixed_versions,
                sources=advisory.get("sources", []),
            )
        )

    return findings


def query_osv(package: str, version: str) -> list:
    response = None

    for attempt in range(2):
        try:
            response = requests.post(
                OSV_URL,
                json={
                    "version": version,
                    "package": {
                        "name": package,
                        "ecosystem": "Packagist",
                    },
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            findings = []

            for vulnerability in data.get("vulns", []):
                references = [
                    ref["url"]
                    for ref in vulnerability.get("references", [])
                    if ref.get("url")
                ]
                findings.append(
                    Finding(
                        advisory_id=vulnerability.get("id", "unknown"),
                        component=package,
                        severity="unknown",
                        affected=True,
                        installed=version,
                        fixed_in=[],
                        sources=references,
                    )
                )

            return findings

        except (requests.RequestException, ValueError):
            if attempt == 1:
                raise

    raise RuntimeError("OSV.dev request failed.")


agent = Agent(
    name="dependency-fix-advisory",
    seed=os.environ.get("ADVISORY_SEED", "dev-only-change-me-advisory"),
    port=8003,
    mailbox=True,
)


@agent.on_message(AdvisoryRequest)
async def on_request(ctx: Context, sender: str, msg: AdvisoryRequest):
    if os.environ.get("USE_MOCKS") == "1":
        await ctx.send(sender, mock_advisory(msg))
        return

    try:
        findings = []

        if msg.php_constraint and not msg.php_version:
            # A constraint is not the deployed PHP runtime version.
            if msg.packages:
                for package, version in msg.packages.items():
                    findings.extend(query_osv(package, version))
            await ctx.send(
                sender,
                AdvisoryResult(
                    session_id=msg.session_id,
                    ok=False,
                    error="Could not verify PHP core: repository provides only a PHP constraint.",
                    findings=findings,
                ),
            )
            return

        advisories = load_advisories()

        if msg.php_version:
            findings.extend(check_php_version(msg.php_version, advisories))

        for package, version in msg.packages.items():
            findings.extend(query_osv(package, version))

        await ctx.send(
            sender,
            AdvisoryResult(
                session_id=msg.session_id,
                ok=True,
                findings=findings,
            ),
        )

    except (OSError, ValueError, KeyError, TypeError, requests.RequestException) as exc:
        await ctx.send(
            sender,
            AdvisoryResult(
                session_id=msg.session_id,
                ok=False,
                error=f"Advisory check failed: {exc}",
            ),
        )


if __name__ == "__main__":
    agent.run()
