# Team briefing: Dependency Fix Crew

Team: Junaid (Dev A), Musthafa (Dev B), Falahi (Dev C). Read intent/ and TEAM.md too.

## Goal
In one ASI:One chat a user asks "Am I affected by the PHP vulnerability from Oct 21? I run PHP
8.3.31" (or gives a repo). Four agents on Agentverse, with the ASI1 LLM reasoning, return a
verdict, a fix plan, and (after approval) a filed GitHub issue.

Judges need: agents registered on Agentverse, ACP, usable in ASI:One, real tool use or
multi-agent work, whole flow in one chat, public repo with instructions. Bonus: Cards, Payment
Protocol, reliability.

## Roles
| Person | Role | Files | Features |
|---|---|---|---|
| Junaid | Concierge | `agents/concierge.py` | ACP + ack every message; ASI1 parses repo vs version; calls Scanner -> Advisory; asks approval; calls Fixer; Cards with text fallback; Agentverse registration; ASI:One shared chat |
| Musthafa | Scanner + Advisory | `agents/scanner.py`, `agents/advisory.py`, `data/advisories.json` | Version input or GitHub read of composer files (timeout + retry); version vs fixed-version comparison (8.3.31 < 8.3.36 = affected); OSV.dev lookup with fallback; errors never become "safe"; tests; verify PHP2Shell entry |
| Falahi | Fixer + submission | `agents/fixer.py`, `README.md` | ASI1 writes plan + issue text; files issue only if `file_issue` is true; returns link or clear error; test repo + token; README, video, dashboard submission; Payment only if time allows |

## How we work
- Branches: `dev-a/concierge`, `dev-b/scanner-advisory`, `dev-c/fixer`. Never push to `main`.
- Small pull requests, each reviewed by a teammate (Junaid by Musthafa, Musthafa by Falahi,
  Falahi by Junaid).
- `agents/models.py` is the contract. Change it only if all three agree.
- `USE_MOCKS=1` runs your agent without the others.
- Own `.env`, own seed per agent. Never commit secrets.
- Say in chat when blocked, when you merge, when you need a review.
- ~T+5h: all three integrate with `USE_MOCKS=0`. ~T+8h: feature freeze, then fixes, README,
  video, submission.

## Priorities
Must have: Phases 0-4 + submission. Cut first: Payment, card polish, extra reliability.

## Rules that protect the demo
- Never say "not affected" when a check failed: say "could not verify".
- Never file an issue without explicit approval in the chat.
