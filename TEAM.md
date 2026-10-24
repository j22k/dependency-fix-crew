# Team workflow (3 people)

## Principle: own an agent, contribute to all of them
Split by agent so nobody blocks anyone, then cross-review and pair on integration so everyone
touches everything.

| Dev | Owns | Phases | Also leads |
|---|---|---|---|
| A | `concierge.py`: ACP, mailbox, ASI1 intent, Cards | 0, 1, 5 | Agentverse registration, ASI:One shared chat |
| B | `scanner.py`, `advisory.py`, `data/advisories.json` | 2, 6 | Reliability and tests |
| C | `fixer.py`, GitHub issue, Payment (optional) | 4, 7 | README, demo video, dashboard submission |

## How everyone contributes to all parts
1. **Contract first (first 20 min, all three):** agree `agents/models.py`. After that, each person
   builds against `agents/mocks.py` with `USE_MOCKS=1`, so no one waits.
2. **Branches:** `dev-a/concierge`, `dev-b/scanner-advisory`, `dev-c/fixer`. Small PRs to `main`.
3. **Cross-review:** A reviews C, B reviews A, C reviews B. Each PR needs one other person.
4. **Pair on integration (Phase 3, all three):** replace mocks with real calls together.
5. **Swap tasks mid-day:** after first integration, rotate bug fixes so each person debugs an agent
   they did not write.
6. **Shared deliverables:** each records their own segment of the demo video and writes their
   agent's section of the README.

## Sync points
- Phase 0 gate: one person drives, all watch, everyone gets their own `.env` working.
- Phase 3 integration, feature freeze (T+8:00), then submission together.

## If one person is blocked or behind
Hand the unfinished piece to whoever is free. Priority is Phases 0-4 + 8; cut Phase 7 first.

## Alternative splits
- **By phase (you take 3 phases, others take the rest):** works, but Phases 3 and 8 depend on
  everyone's output and the Concierge sits on the critical path. Prefer the by-agent split.
- **Pair + solo:** two people on the Concierge/ASI:One path (highest risk), one on Scanner+Advisory,
  Fixer picked up by whoever finishes first. Use this if the Phase 0 gate is troublesome.
