"""Standalone interactive demo test script for Fixer agent.

Sends FixRequests directly to the running Fixer agent using uAgents messaging.
Demonstrates:
  1. Remediation plan generation (file_issue=False)
  2. Plan inspection & interactive confirmation
  3. GitHub issue creation (file_issue=True)
"""
import asyncio
import os
import uuid

import aiohttp
from dotenv import load_dotenv
from uagents import Agent
from uagents.query import send_sync_message
from uagents_core.types import MsgStatus

from agents.models import Finding, FixRequest, FixResult

load_dotenv()

# Initialize event loop for Python 3.14 compatibility if needed
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


def get_fixer_address() -> str:
    """Resolve Fixer agent address from .env or calculate from FIXER_SEED."""
    address = os.environ.get("FIXER_ADDRESS", "").strip()
    if not address:
        seed = os.environ.get("FIXER_SEED", "dev-only-change-me-fixer")
        temp_agent = Agent(seed=seed, name="temp-address-resolver")
        address = temp_agent.address
    return address


async def run_demo():
    fixer_address = get_fixer_address().removeprefix("agent://")
    resolver = None  # Use the default uAgents resolver

    demo_repo = os.environ.get("DEMO_REPO", "").strip()
    if not demo_repo:
        print("Note: DEMO_REPO is not set in .env.")
        demo_repo = input(
            "Enter target GitHub repository (owner/repo) [default: test-owner/test-repo]: "
        ).strip()
        if not demo_repo:
            demo_repo = "test-owner/test-repo"
    session_id = f"demo-{uuid.uuid4().hex[:8]}"

    # Mock finding for a clearly labelled test vulnerability
    finding = Finding(
        advisory_id="TEST-PHP2Shell-CVE-2026-109618",
        component="php-core",
        severity="critical",
        affected=True,
        installed="8.3.31",
        fixed_in=["8.5.12", "8.4.27", "8.3.36", "8.2.35"],
        sources=["https://unit42.paloaltonetworks.com/cve-2026-109618-cve-2026-109619/"],
    )

    print("\n" + "=" * 60)
    print("FIXER DEMO TEST RUNNER")
    print("=" * 60)
    print(f"Fixer Agent Address : {fixer_address}")
    print("Fixer Endpoint      : Default uAgents resolver")
    print(f"Target Repository   : {demo_repo}")
    print(f"Session ID          : {session_id}")
    print(f"Test Vulnerability  : {finding.advisory_id} ({finding.component} {finding.installed})")
    print("=" * 60)

    # Step 1: Request remediation plan (file_issue=False)
    print("\n[Step 1/2] Requesting remediation plan from Fixer (file_issue=False)...")
    req_plan = FixRequest(
        session_id=session_id,
        target=demo_repo,
        findings=[finding],
        file_issue=False,
    )

    try:
        res1 = await send_sync_message(
            destination=fixer_address,
            message=req_plan,
            response_type=FixResult,
            resolver=resolver,
            timeout=30,
        )
    except (aiohttp.ClientError, ConnectionError, TimeoutError, OSError, RuntimeError) as e:
        print(f"\n[Error] Could not connect to Fixer at {"Default uAgents resolver"}: {e}")
        print("Make sure Fixer is running in another terminal via: make run-fixer\n")
        return

    if isinstance(res1, MsgStatus) or not isinstance(res1, FixResult):
        detail = getattr(res1, "detail", str(res1))
        print(f"\n[Error] Could not reach Fixer agent at {"Default uAgents resolver"}: {detail}")
        print("Make sure Fixer is running in another terminal via: make run-fixer\n")
        return

    if not res1.ok:
        print(f"\n[Error] Fixer returned an error: {res1.error}")
        return

    print("\n" + "-" * 60)
    print("REMEDIATION PLAN RECEIVED:")
    print("-" * 60)
    print(res1.plan_markdown)
    print("-" * 60)

    # Step 2: Explicit confirmation before issue filing
    print("\n[Step 2/2] GitHub Issue Creation Confirmation")
    confirm = input(
        f"Do you want to create a GitHub issue on '{demo_repo}'? [y/N]: "
    ).strip().lower()

    if confirm not in ("y", "yes"):
        print("\nSkipping issue creation. Demo completed safely without modifying GitHub.\n")
        return

    print(f"\nSending issue creation request to Fixer for session '{session_id}' (file_issue=True)...")
    req_issue = FixRequest(
        session_id=session_id,
        target=demo_repo,
        findings=[finding],
        file_issue=True,
    )

    try:
        res2 = await send_sync_message(
            destination=fixer_address,
            message=req_issue,
            response_type=FixResult,
            resolver=resolver,
            timeout=30,
        )
    except (aiohttp.ClientError, ConnectionError, TimeoutError, OSError, RuntimeError) as e:
        print(f"\n[Error] Communication error during issue creation: {e}")
        return

    if isinstance(res2, MsgStatus) or not isinstance(res2, FixResult):
        detail = getattr(res2, "detail", str(res2))
        print(f"\n[Error] Could not communicate with Fixer agent: {detail}")
        return

    print("\n" + "=" * 60)
    if res2.ok:
        print("GITHUB ISSUE CREATED SUCCESSFULLY!")
        print(f"Issue URL: {res2.issue_url}")
    else:
        print("FAILED TO CREATE GITHUB ISSUE")
        print(f"Error: {res2.error}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
