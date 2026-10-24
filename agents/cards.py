"""ASI1 Interactive Cards for the Concierge (owner: Dev A).

Card = a normal ChatMessage with a TextContent narration (our plain-text fallback, always
complete on its own) plus one MetadataContent block. All metadata values must be strings;
card_protocol_version is mandatory or ASI:One silently drops the card.
Schema source: innovationlab.fetch.ai interactive-cards docs (review card).
"""
import json
import os
from typing import List

from uagents_core.contrib.protocols.chat import ChatMessage, MetadataContent, TextContent

from agents.models import Finding


def cards_on() -> bool:
    return os.environ.get("CARDS", "1") != "0"


def build_card_message(narration: str, card_kind: str, payload: dict) -> ChatMessage:
    return ChatMessage(
        content=[
            TextContent(type="text", text=narration),
            MetadataContent(
                type="metadata",
                metadata={
                    "card_protocol_version": "1",
                    "requires_card_interaction": "true",
                    "card_kind": card_kind,
                    "card_payload": json.dumps(payload),
                },
            ),
        ]
    )


def review_payload(session_id: str, findings: List[Finding], plan: str) -> dict:
    rows = []
    for f in findings:
        status = "AFFECTED" if f.affected else "not affected"
        fixed = ", ".join(f.fixed_in) or "no fixed version listed"
        rows.append({
            "label": f"{f.component} {f.installed}",
            "value": f"{f.advisory_id}: {status} ({f.severity}). Fixed in: {fixed}",
        })
    rows.append({"label": "Plan", "value": plan.replace("\n", " ")[:300]})
    return {
        "title": "Vulnerability check result",
        "summary_rows": rows,
        "approve_cta": {
            "label": "File GitHub issue",
            "selection": {"action": "approve_issue", "session_id": session_id},
            "primary": True,
        },
        "reject_cta": {
            "label": "Not now",
            "selection": {"action": "reject_issue", "session_id": session_id},
        },
    }


def review_card(narration: str, session_id: str, findings: List[Finding], plan: str) -> ChatMessage:
    return build_card_message(narration, "review", review_payload(session_id, findings, plan))
