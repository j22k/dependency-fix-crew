# GEMINI.md

Dependency Fix Crew: a multi-agent system on Agentverse, used through ASI:One.

Before changing anything, read:
- `intent/spec.md`
- `intent/plan.md`

## Commands

- Setup: `python -m venv .venv`, activate the virtual environment, then run `pip install -r requirements.txt`.
- Run Concierge: `make run-concierge`
- Run Scanner: `make run-scanner`
- Run Advisory: `make run-advisory`
- Run Fixer: `make run-fixer`
- Test: `make test`
- Lint: `make lint`

## Conventions

- Keep one uAgent per file in `agents/`.
- Shared message models live only in `agents/models.py`.
- Changes to `agents/models.py` require agreement from all three owners because it is the team contract. Do not change shared models unilaterally.
- Load secrets only from `.env` using `python-dotenv`. Never hardcode API keys, tokens, or agent seeds.
- Use `uagents==0.25.5`.
- Import chat protocols from `uagents_core.contrib.protocols.chat`.
- If implementation changes or drifts from `intent/plan.md`, update `intent/plan.md` in the same commit.
- Every requirement with an R-number in `intent/spec.md` must have a test or a documented manual check.

## Architecture

- Only the Concierge communicates with ASI:One using ACP.
- Scanner, Advisory, and Fixer communicate with the Concierge using typed `Model` messages. They must not communicate directly with ASI:One.
- Use `agents/mocks.py` to develop an agent before neighboring agents are available. Set `USE_MOCKS=1` for mock-based development.
- Access the ASI1 LLM through the `openai` client, using base URL `https://api.asi1.ai/v1` and model `asi1`.

## Important implementation requirements

- Every ACP handler must send a `ChatAcknowledgement`, and an acknowledgement handler must exist.
- Interactive Card metadata values must all be strings. Encode nested values as JSON strings.
- Include `card_protocol_version`; omitting it can cause the card to be silently dropped.
- Always provide a plain-text fallback when using Interactive Cards.
- Never report a result as “not affected” if a check failed. Report that it “could not be verified.”
- Never file a GitHub issue without explicit user approval in the chat.
- Never commit `.env`, agent seeds, tokens, or other secrets.
- Give each agent its own seed; do not reuse seeds between agents.

## Working practices

- Inspect the existing code and the two intent documents before editing.
- Prefer small, focused changes that fit the existing architecture.
- Avoid changing unrelated files or introducing new frameworks/dependencies without team agreement.
- Add or update tests for changed behavior, and run `make test` and `make lint` when practical.
- Use mocks when dependent agents are not ready, and clearly distinguish mock behavior from real integrations.
- Before committing, review `git diff` and `git status`. Ensure no secrets or unrelated changes are included.
- Work on your assigned Git branch and do not merge into `main` without the required review.
- If the implementation requires changing shared models or deviating from the plan, stop and get team agreement before proceeding.

## Gemini CLI guidance

- Treat this file as the repository's project instructions.
- Follow the instructions in `intent/spec.md` and `intent/plan.md`; do not invent requirements that are not documented there.
- Before making a substantial change, summarize the intended files and approach, and flag any assumptions or contract changes.
- If required information is missing or conflicting, ask for clarification rather than silently choosing an interpretation.
- After making changes, summarize what changed, which tests/checks were run, and any remaining issues.
