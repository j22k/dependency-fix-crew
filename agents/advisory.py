"""Advisory Researcher (owner: Dev B). Matches versions to advisories (local file + OSV.dev)."""
import os

from dotenv import load_dotenv
from uagents import Agent, Context

from agents.mocks import mock_advisory
from agents.models import AdvisoryRequest, AdvisoryResult

load_dotenv()
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
    # TODO(Dev B): load data/advisories.json; compare php_version to fixed_in per branch
    #              (8.3.31 < 8.3.36 -> affected; branches < 8.2 are EOL with no fix).
    # TODO(Dev B): OSV.dev query for packages (retry, timeout, cached fallback).
    # On any failed check return ok=False so the Concierge says "could not verify".
    await ctx.send(sender, AdvisoryResult(session_id=msg.session_id, ok=False, error="not implemented"))


if __name__ == "__main__":
    agent.run()
