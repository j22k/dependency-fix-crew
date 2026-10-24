# CLAUDE.md

Dependency Fix Crew: multi-agent system on Agentverse, used through ASI:One. Read intent/spec.md
and intent/plan.md before changing anything.

## Commands
- Setup: `python -m venv .venv`, activate it, `pip install -r requirements.txt`
- Run Concierge: `make run-concierge` (also `run-scanner`, `run-advisory`, `run-fixer`)
- Test: `make test`
- Lint: `make lint`

## Conventions
- One uAgent per file in `agents/`. Shared message models live only in `agents/models.py`.
- Changing a model in `models.py` needs all three owners to agree (it is the team contract).
- Secrets only from `.env` via python-dotenv. Never hardcode keys or seeds.
- Use `uagents==0.25.5`. Chat imports come from `uagents_core.contrib.protocols.chat`.
- Update `intent/plan.md` in the same commit if the implementation drifts from it.
- Every requirement R-number in spec.md needs a test or a documented manual check.

## Architecture
- Only the Concierge speaks ACP to ASI:One. Scanner, Advisory and Fixer talk to the Concierge
  with typed Model messages and never to ASI:One.
- Use `agents/mocks.py` to develop an agent before its neighbors exist (`USE_MOCKS=1`).
- ASI1 LLM via the `openai` client, base URL `https://api.asi1.ai/v1`, model `asi1`.

## Things Claude gets wrong
- Every ACP handler must send a `ChatAcknowledgement`, and the ack handler must exist.
- Interactive Card metadata values must all be strings; nested values are JSON-encoded;
  omitting `card_protocol_version` drops the card silently. Always keep a plain-text fallback.
- Never say "not affected" when a check failed. Say "could not verify".
- Never file a GitHub issue without explicit user approval in the chat.
- Never commit `.env`, seeds, or tokens. Each agent gets its own seed.
