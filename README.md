# Dependency Fix Crew

Fetch-A-Thon 3.0 submission: ASI:One Agent Challenge, "From Intent to Action".

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

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
| Concierge | ACP entry point, ASI1 reasoning, Cards | `agent1qw8nlqj3xt3ejnhhcf2vmpk5d48sx6n2m4ekms2dd6pxzlg0vdpa7v6m9mg` | https://agentverse.ai/agents/details/agent1qw8nlqj3xt3ejnhhcf2vmpk5d48sx6n2m4ekms2dd6pxzlg0vdpa7v6m9mg/profile |
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

## Extra resources needed to run
- ASI:One account and API key: https://asi1.ai/ (Developer section)
- Agentverse account (mailbox, profiles): https://agentverse.ai
- GitHub personal access token with permission to create issues on `DEMO_REPO` (Fixer)
- Python 3.10+, packages in `requirements.txt` (`uagents==0.25.5`, `openai`, `python-dotenv`)
- Docs we followed:
  - Chat protocol: https://docs.agentverse.ai/documentation/getting-started/enable-chat-protocol
  - ASI:One-compatible uAgent: https://uagents.fetch.ai/docs/examples/asi-1
  - Interactive Cards: https://innovationlab.fetch.ai/resources/docs/interactive-cards/asi-interactive-cards
  - Hackpack: https://innovationlab.fetch.ai/events/hackathons/fetch-a-thon-3/hackpack

## Agentverse agent READMEs
Each agent's profile README (with the Innovation Lab and hackathon badges) is kept in
`agent-readmes/`. Paste each into that agent's README on Agentverse.

## Data sources and limits
Advisory data for PHP core is a cited local file (`data/advisories.json`); Composer packages use
OSV.dev. If a check fails the agent says "could not verify" rather than "safe".

## Team
TODO names. See TEAM.md for the work split.
