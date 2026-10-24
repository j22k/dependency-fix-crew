# Plan: Dependency Fix Crew (from intent.md and spec.md)

Status: DRAFT. Update this file in the same commit if the code drifts from it.
Owners: A = Concierge/ASI:One, B = Scanner/Advisory, C = Fixer/GitHub/Submission.

## Order of work

| Phase | Work | Owner | Reqs | Proof |
|---|---|---|---|---|
| 0 | Accounts, keys, run docs' minimal example, reach it from asi1.ai. GATE. | All (A drives) | R1-R3 | Example agent answers in ASI:One |
| 0.5 | Freeze `agents/models.py` contracts + `mocks.py` | All, 20 min | R7 | All three can run against mocks |
| 1 | Concierge: ACP, mailbox, manifest, ASI1 intent parsing | A | R1-R3, R8 | Message in ASI:One returns parsed task |
| 2 | Scanner: GitHub file read + version-string input | B | R4 | `test_scanner.py` |
| 2 | Advisory: match against `advisories.json` + OSV.dev | B | R4 | "8.3.31" -> affected, fix 8.3.36 |
| 4 | Fixer: ASI1 plan + issue text, GitHub issue on approval | C | R4, R8, R12 | Real issue on test repo |
| 3 | Wire agents together (replace mocks) | All (pair) | R7 | Logs show 4 agents exchanging messages |
| 5 | Cards: verdict + review/approve, text fallback | A | R10 | Playground-valid payloads render |
| 6 | Retries, timeouts, "could not verify" paths | B + C | R9, R12 | Tests with forced failures |
| 7 | Payment Protocol (optional, cut first) | C | R11 | Per-scan request/complete flow |
| 8 | README, shared chat URL, video, dashboard submission | All, C leads | R6 | Links verified |

Cut order if short on time: Phase 7, then card polish, then extra reliability.
Minimum viable: Phases 0-4 + 8.

## Files that change
- agents/*.py, agents/models.py, data/advisories.json, tests/*, README.md

## Risks
- Phase 0 fails: nothing else matters, fix first.
- PHP core not in OSV.dev: use cited local entry.
- ASI:One chat may not accept file uploads: use repo URL or pasted text.
- Card details and payment setup unverified: read docs before building.
- Mailbox needs the Concierge running during the demo.

## Integration points (team sync)
- T+0:45 Phase 0 gate passed
- T+1:15 contracts frozen
- T+5:00 first end-to-end integration
- T+8:00 feature freeze, only fixes and submission
