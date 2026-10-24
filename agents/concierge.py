"""Concierge (owner: Dev A). The only agent that speaks ACP to ASI:One.

Phase 1: ACP + mailbox + manifest + ASI1 intent parsing. Phase 3: orchestrate the other agents.
Phase 5: Interactive Cards. Skeleton follows the Innovation Lab ASI:One-compatible agent guide.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement, ChatMessage, TextContent, chat_protocol_spec,
)

from agents.models import AdvisoryResult, FixResult, ScanResult

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


@chat.on_message(ChatMessage)
async def on_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(acknowledged_msg_id=msg.msg_id))
    text = "".join(c.text for c in msg.content if isinstance(c, TextContent))
    # TODO(Dev A): ASI1 parses text -> {kind, target}; send ScanRequest to the Scanner.
    # TODO(Dev A): on verdict send a card (Phase 5); on user approval send FixRequest.
    reply = f"Received: {text}"
    await ctx.send(sender, ChatMessage(content=[TextContent(type="text", text=reply)]))


@chat.on_message(ChatAcknowledgement)
async def on_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


@agent.on_message(ScanResult)
async def on_scan(ctx: Context, sender: str, msg: ScanResult):
    pass  # TODO(Dev A): forward to Advisory


@agent.on_message(AdvisoryResult)
async def on_advisory(ctx: Context, sender: str, msg: AdvisoryResult):
    pass  # TODO(Dev A): build verdict, ask user to approve


@agent.on_message(FixResult)
async def on_fix(ctx: Context, sender: str, msg: FixResult):
    pass  # TODO(Dev A): return plan + issue link to the user


agent.include(chat, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
