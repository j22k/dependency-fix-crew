"""Fixer (owner: Dev C). Writes the remediation plan with ASI1 and files a GitHub issue on approval."""
import os

from dotenv import load_dotenv
from uagents import Agent, Context

from agents.mocks import mock_fix
from agents.models import FixRequest, FixResult

load_dotenv()
agent = Agent(
    name="dependency-fix-fixer",
    seed=os.environ.get("FIXER_SEED", "dev-only-change-me-fixer"),
    port=8004,
    mailbox=True,
)


@agent.on_message(FixRequest)
async def on_fix(ctx: Context, sender: str, msg: FixRequest):
    if os.environ.get("USE_MOCKS") == "1":
        await ctx.send(sender, mock_fix(msg))
        return
    # TODO(Dev C): ASI1 writes plan_markdown + issue body from msg.findings.
    # TODO(Dev C): only if msg.file_issue is True, POST the issue to msg.target via the GitHub API;
    #              retry on transient errors; return issue_url or a clear error.
    await ctx.send(sender, FixResult(session_id=msg.session_id, ok=False, error="not implemented"))


if __name__ == "__main__":
    agent.run()
