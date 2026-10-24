"""Scanner (owner: Dev B). Reads a repo's composer files / PHP version, or accepts a version string."""
import os

from dotenv import load_dotenv
from uagents import Agent, Context

from agents.mocks import mock_scan
from agents.models import ScanRequest, ScanResult

load_dotenv()
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
    # TODO(Dev B): kind == "version" -> return it as php_version.
    # TODO(Dev B): kind == "repo" -> GitHub API: composer.json / composer.lock; retry + timeout;
    #              on failure send ScanResult(ok=False, error=...), never guess.
    await ctx.send(sender, ScanResult(session_id=msg.session_id, ok=False, error="not implemented"))


if __name__ == "__main__":
    agent.run()
