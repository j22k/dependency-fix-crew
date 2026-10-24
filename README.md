# Dependency Fix Crew

Fetch-A-Thon 3.0 submission: ASI:One Agent Challenge, "From Intent to Action".

> TODO: add the Innovation Lab and hackathon badges required by the hackpack.

## Problem
When a critical vulnerability lands (for example PHP2Shell, CVE-2026-109618 / CVE-2026-109619,
patched 21 Oct 2026), teams scramble to find out whether they are affected and what to upgrade to.

## What it does
Ask in ASI:One: "Am I affected by the PHP vulnerability from Oct 21? I run PHP 8.3.31" or give a
repo URL. The crew returns a verdict, a remediation plan, and (after your approval) files a
GitHub issue.

## Agents (registered on Agentverse)
| Agent | Role | Address | Agentverse profile |
|---|---|---|---|
| Concierge | ACP entry point, ASI1 reasoning, Cards | `TODO agent1q...` | TODO |
| Scanner | Reads repo / version | `TODO` | TODO |
| Advisory | Matches advisories | `TODO` | TODO |
| Fixer | Plan + GitHub issue | `TODO` | TODO |

## Architecture
```
User -> ASI:One -> Concierge (ACP + ASI1)
                      |-> Scanner -> Advisory -> verdict card
                      |-> (user approves) -> Fixer -> GitHub issue -> link in chat
```

## Setup
1. Python 3.10+, `python -m venv .venv`, activate it.
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in `ASI1_API_KEY`, `GITHUB_TOKEN`, seeds.
4. Run each agent in its own terminal: `make run-concierge`, `run-scanner`, `run-advisory`,
   `run-fixer` (or `python -m agents.concierge`).
5. Open the inspector link printed by the Concierge, choose Mailbox, then **Chat with Agent**.

## Test
- `make test`
- Manual: in asi1.ai ask "Am I affected by the PHP vulnerability from Oct 21? I run PHP 8.3.31".
  Expected: affected, upgrade to 8.3.36.
- Use `USE_MOCKS=1` to run one agent without the others.

## Shared demo
- ASI:One shared chat: TODO
- Demo video: TODO

## Data sources and limits
Advisory data for PHP core is a cited local file (`data/advisories.json`); Composer packages use
OSV.dev. If a check fails the agent says "could not verify" rather than "safe".

## Team
TODO names. See TEAM.md for the work split.
