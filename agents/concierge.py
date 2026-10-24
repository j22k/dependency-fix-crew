"""Concierge (owner: Dev A). The only agent that speaks ACP to ASI:One.

Phase 1 flow: chat text -> ASI1 intent -> Scanner -> Advisory -> Fixer (plan) -> ask approval ->
Fixer (file issue) -> reply. Plain-text replies for now; Interactive Cards are Phase 5.
With USE_MOCKS=1 the downstream steps are answered in-process from agents/mocks.py, so the
Concierge can be demoed alone.
"""
import asyncio
import os
import uuid
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement, ChatMessage, TextContent, chat_protocol_spec,
)

from agents import mocks
from agents.cards import cards_on, review_card
from agents.intent import (
    INTENT_PROMPT, extract_repo, is_approval, is_rejection, parse_llm_json, parse_selection,
    regex_intent,
)
from agents.models import (
    AdvisoryRequest, AdvisoryResult, FixRequest, FixResult, ScanRequest, ScanResult,
)

load_dotenv()
llm = OpenAI(base_url="https://api.asi1.ai/v1", api_key=os.environ.get("ASI1_API_KEY", ""))

agent = Agent(
    name="dependency-fix-concierge",
    seed=os.environ.get("CONCIERGE_SEED", "dev-only-change-me"),
    port=8001,
    mailbox=True,
    publish_agent_details=True,
)
chat = Protocol(spec=chat_protocol_spec)

SESSIONS: Dict[str, dict] = {}  # session_id -> state
PENDING: Dict[str, str] = {}  # user address -> session_id awaiting approval

HELP = (
    "I check whether a known vulnerability affects you and help you fix it. Tell me the PHP "
    "version you run (for example: 'Am I affected by the PHP vulnerability from Oct 21? "
    "I run PHP 8.3.31') or give a GitHub repo."
)


LABELS = {"SCANNER_ADDRESS": "Scanner", "ADVISORY_ADDRESS": "Advisory", "FIXER_ADDRESS": "Fixer"}
_TASKS: set = set()  # keep references so watchdog tasks are not garbage collected


def mocks_on() -> bool:
    return os.environ.get("USE_MOCKS") == "1"


def timeout_s() -> float:
    return float(os.environ.get("DOWNSTREAM_TIMEOUT_S", "30"))


async def watchdog(ctx: Context, session_id: str, token: int, label: str):
    """If no reply arrives for this step in time, tell the user instead of waiting forever."""
    await asyncio.sleep(timeout_s())
    s = SESSIONS.get(session_id)
    if s and s.get("token") == token:
        await fail(ctx, session_id, f"the {label} agent did not respond in time.")


async def say(ctx: Context, user: str, text: str):
    await ctx.send(user, ChatMessage(content=[TextContent(type="text", text=text)]))


async def fail(ctx: Context, session_id: str, reason: str):
    s = SESSIONS.pop(session_id, None)
    if s:
        PENDING.pop(s["user"], None)
        await say(ctx, s["user"], f"I could not verify this: {reason}")


def _llm_intent(text: str):
    resp = llm.chat.completions.create(
        model="asi1",
        messages=[{"role": "system", "content": INTENT_PROMPT}, {"role": "user", "content": text}],
        max_tokens=100,
    )
    return parse_llm_json(resp.choices[0].message.content)


async def understand(ctx: Context, text: str):
    """ASI1 reads the intent; a regex fallback keeps the flow alive if the LLM call fails."""
    try:
        parsed = await asyncio.to_thread(_llm_intent, text)
        if parsed:
            return parsed
    except Exception as exc:  # network, auth, rate limit
        ctx.logger.warning(f"ASI1 intent call failed, using fallback: {exc}")
    return regex_intent(text)


async def dispatch(ctx: Context, session_id: str, env_name: str, request, mock_fn):
    if mocks_on():
        await handle_result(ctx, mock_fn(request))
        return
    address = os.environ.get(env_name, "")
    if not address:
        await fail(ctx, session_id, f"{env_name} is not configured.")
        return
    s = SESSIONS.get(session_id)
    if s is not None:
        s["token"] = s.get("token", 0) + 1
        task = asyncio.create_task(watchdog(ctx, session_id, s["token"], LABELS.get(env_name, env_name)))
        _TASKS.add(task)
        task.add_done_callback(_TASKS.discard)
    await ctx.send(address, request)


async def handle_result(ctx: Context, msg):
    if isinstance(msg, ScanResult):
        await on_scan_result(ctx, msg)
    elif isinstance(msg, AdvisoryResult):
        await on_advisory_result(ctx, msg)
    elif isinstance(msg, FixResult):
        await on_fix_result(ctx, msg)


def verdict_text(findings) -> str:
    lines = []
    for f in findings:
        status = "AFFECTED" if f.affected else "not affected"
        fixed = ", ".join(f.fixed_in) or "no fixed version listed"
        src = f" Source: {f.sources[0]}" if f.sources else ""
        lines.append(f"- {f.advisory_id} ({f.component} {f.installed}): {status}, {f.severity}. "
                     f"Fixed in: {fixed}.{src}")
    return "\n".join(lines)


async def on_scan_result(ctx: Context, msg: ScanResult):
    if msg.session_id not in SESSIONS:
        return
    if not msg.ok:
        await fail(ctx, msg.session_id, msg.error or "the scan failed.")
        return
    if not msg.php_version and not msg.packages:
        await fail(ctx, msg.session_id, "I could not determine the PHP version or packages.")
        return
    req = AdvisoryRequest(session_id=msg.session_id, php_version=msg.php_version, packages=msg.packages)
    await dispatch(ctx, msg.session_id, "ADVISORY_ADDRESS", req, mocks.mock_advisory)


async def on_advisory_result(ctx: Context, msg: AdvisoryResult):
    s = SESSIONS.get(msg.session_id)
    if not s:
        return
    if not msg.ok:
        await fail(ctx, msg.session_id, msg.error or "the advisory check failed.")
        return
    s["findings"] = msg.findings
    if not any(f.affected for f in msg.findings):
        SESSIONS.pop(msg.session_id, None)
        text = "No advisory in my data matches what you run."
        if msg.findings:
            text += "\n" + verdict_text(msg.findings)
        await say(ctx, s["user"], text + "\nThis only covers the advisories I know about.")
        return
    req = FixRequest(session_id=msg.session_id, target=s["repo"], findings=msg.findings, file_issue=False)
    await dispatch(ctx, msg.session_id, "FIXER_ADDRESS", req, mocks.mock_fix)


async def on_fix_result(ctx: Context, msg: FixResult):
    s = SESSIONS.get(msg.session_id)
    if not s:
        return
    if not msg.ok:
        await fail(ctx, msg.session_id, msg.error or "I could not prepare the fix.")
        return
    if msg.issue_url:
        SESSIONS.pop(msg.session_id, None)
        PENDING.pop(s["user"], None)
        await say(ctx, s["user"], f"Done. Issue filed: {msg.issue_url}")
        return
    s["plan"] = msg.plan_markdown
    s["token"] = s.get("token", 0) + 1  # waiting on the user now, not a downstream agent
    PENDING[s["user"]] = msg.session_id
    text = (
        f"Verdict:\n{verdict_text(s['findings'])}\n\nPlan:\n{msg.plan_markdown}\n\n"
        "Reply 'yes' to file this as a GitHub issue, or 'no' to stop."
    )
    if cards_on():
        # The narration is the complete plain-text fallback if the card is not rendered.
        await ctx.send(s["user"], review_card(text, msg.session_id, s["findings"], msg.plan_markdown))
    else:
        await say(ctx, s["user"], text)


async def handle_approval(ctx: Context, user: str, session_id: str, text: str) -> bool:
    """Return True if the message was consumed as part of the pending approval."""
    s = SESSIONS.get(session_id)
    if not s:
        PENDING.pop(user, None)
        return False
    if is_rejection(text):
        SESSIONS.pop(session_id, None)
        PENDING.pop(user, None)
        await say(ctx, user, "Okay, I won't file anything.")
        return True
    if s.get("awaiting_repo"):
        repo = extract_repo(text)
        if not repo:
            if regex_intent(text)[0] != "unknown":  # a fresh request, not the repo answer
                PENDING.pop(user, None)
                SESSIONS.pop(session_id, None)
                return False
            await say(ctx, user, "Which repo (owner/name) should I file the issue in?")
            return True
    elif is_approval(text):
        repo = extract_repo(text) or s["repo"] or os.environ.get("DEMO_REPO", "")
        if not repo:
            s["awaiting_repo"] = True
            await say(ctx, user, "Which repo (owner/name) should I file the issue in?")
            return True
    else:
        PENDING.pop(user, None)  # a new request, not an answer
        return False
    s["awaiting_repo"] = False
    req = FixRequest(session_id=session_id, target=repo, findings=s["findings"], file_issue=True)
    await dispatch(ctx, session_id, "FIXER_ADDRESS", req, mocks.mock_fix)
    return True


@chat.on_message(ChatMessage)
async def on_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(acknowledged_msg_id=msg.msg_id))
    text = "".join(c.text for c in msg.content if isinstance(c, TextContent)).strip()
    if not text:
        return
    selection = parse_selection(text)  # a card button click
    if selection:
        text = "yes" if selection["action"] == "approve_issue" else "no"
        sid = selection.get("session_id", "")
        if SESSIONS.get(sid, {}).get("user") == sender:
            PENDING[sender] = sid
    pending = PENDING.get(sender)
    if pending and await handle_approval(ctx, sender, pending, text):
        return
    kind, target = await understand(ctx, text)
    if kind == "unknown" or not target:
        await say(ctx, sender, HELP)
        return
    session_id = uuid.uuid4().hex[:12]
    SESSIONS[session_id] = {
        "user": sender, "kind": kind, "target": target,
        "repo": target if kind == "repo" else "", "findings": [], "plan": "",
    }
    await say(ctx, sender, f"Checking {kind} {target}...")
    await dispatch(ctx, session_id, "SCANNER_ADDRESS",
                   ScanRequest(session_id=session_id, kind=kind, target=target), mocks.mock_scan)


@chat.on_message(ChatAcknowledgement)
async def on_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


@agent.on_message(ScanResult)
async def _scan(ctx: Context, sender: str, msg: ScanResult):
    await on_scan_result(ctx, msg)


@agent.on_message(AdvisoryResult)
async def _advisory(ctx: Context, sender: str, msg: AdvisoryResult):
    await on_advisory_result(ctx, msg)


@agent.on_message(FixResult)
async def _fix(ctx: Context, sender: str, msg: FixResult):
    await on_fix_result(ctx, msg)


agent.include(chat, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
