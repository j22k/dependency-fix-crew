# Spec: Dependency Fix Crew

Source: intent/intent.md | Status: DRAFT | Skills applied: none (hackathon)

## Requirements
Numbered so plan.md and PRs can cite them.

| ID | Requirement | Mandatory? | Judging criterion earned |
|---|---|---|---|
| R1 | At least one agent registered on Agentverse (mailbox, `publish_manifest=True`) | Yes | Fetch.ai tech (20%) |
| R2 | Agent Chat Protocol implemented (ack every message, handle text) | Yes | Fetch.ai tech |
| R3 | Discoverable and usable in ASI:One | Yes | Fetch.ai tech, UX |
| R4 | Real tool execution: GitHub read, advisory match, issue creation | Yes | Functionality (25%) |
| R5 | Full workflow inside one ASI:One chat | Yes | UX (15%) |
| R6 | Public GitHub repo with setup and test instructions | Yes | Submission |
| R7 | Four agents (Concierge, Scanner, Advisory, Fixer) exchange typed messages | Bonus | Fetch.ai tech, Functionality |
| R8 | ASI1 LLM parses intent and writes the plan/issue text | Judged | Fetch.ai tech |
| R9 | Retries, fallbacks, clear errors on failed tool calls | Bonus | Functionality |
| R10 | Interactive Cards: verdict card + review/approve card (text fallback) | Bonus | UX |
| R11 | Payment Protocol per-scan fee | Optional bonus | Fetch.ai tech |
| R12 | Never claim "safe" when a check failed; issue filed only after approval | Quality | Impact |

## Design
- Only the Concierge speaks ACP to ASI:One. The other three agents talk to it with typed
  uAgents `Model` messages (see agents/models.py).
- Flow: Concierge (ASI1 parses intent) -> Scanner -> Advisory -> Concierge verdict card ->
  user approves -> Fixer (ASI1 writes plan + issue) -> files issue -> Concierge returns link.
- Session state keyed by `session_id` held in the Concierge.
- Advisory: local cited `data/advisories.json` for PHP core, OSV.dev for Composer packages.
- Failure handling: every downstream call has a timeout; Concierge reports "could not verify".

## Constraint mapping
| Intent constraint | How met |
|---|---|
| Fetch.ai stack only | uAgents + ACP + ASI1 + Cards (+ Payment) |
| One-chat workflow | Cards + text, no external UI |
| No secrets in repo | `.env` gitignored, `.env.example` committed |

## Open questions carried forward
See intent.md (Payment, input scope, ASI1 limits, OSV coverage).

## Areas of concern
| Concern | Owner |
|---|---|
| PHP core advisory coverage | Dev B |
| ACP + Cards payload validity | Dev A |
| GitHub token scope and rate limits | Dev C |
