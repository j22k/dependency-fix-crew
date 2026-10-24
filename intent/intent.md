# Intent: Dependency Fix Crew

Status: DRAFT for team review (Fetch-A-Thon 3.0, 24 Oct 2026)

## Problem
When a critical vulnerability is disclosed, engineering teams scramble to work out which of their
projects and servers are exposed and what to upgrade to. Example: two critical PHP core
remote-code-execution flaws (CVE-2026-109618, CVE-2026-109619, "PHP2Shell") were patched on
21 Oct 2026. Fixed releases: PHP 8.5.12, 8.4.27, 8.3.36, 8.2.35. Alerts are noisy and the fix is
rarely written down in one place.

## Target users
Dev teams, agencies, and hosting providers that run many PHP / Composer projects.

## Outcome the agent produces
In one ASI:One chat the user asks "Am I affected?" (a repo URL or a PHP version string) and gets:
1. A verdict (affected or not, severity, fixed version, source link).
2. A prioritized remediation plan.
3. A drafted GitHub issue, filed on the user's approval, with the issue link returned.

## Systems involved
- Agentverse (registration, profiles), ASI:One (chat + discovery), ASI1 LLM (reasoning)
- Agent Chat Protocol (ACP), uAgents, ASI1 Interactive Cards, Payment Protocol (optional)
- GitHub API (read repo files, create issue)
- Advisory data: OSV.dev for Composer packages (verify coverage) + cited local entry for PHP core
  (`data/advisories.json`)

## Constraints
- Orchestration, reasoning, discovery and payments stay inside the Fetch.ai stack. No extra agent
  framework.
- The whole primary workflow completes inside an ASI:One conversation. No custom frontend.
- Public GitHub repo with run/test instructions. No secrets committed.
- Finish in one day with a team of three.

## Non-goals
- Auto-merging fixes or opening PRs that change code (issue only).
- Scanning private repos without the user's token.
- Replacing a full SCA product.

## Anti-goals (failure even if it "works")
- Telling a user they are safe when we could not check (must say "could not verify").
- Filing an issue without explicit approval.
- A single script pretending to be multi-agent.

## Open questions
- Payment Protocol: include or cut? Docs show a USDC/Skyfire example; setup effort unverified.
- Input scope: repo URL only, or also a plain version string? (Plan: support both.)
- Does ASI1 have usable free rate limits for a live demo? Unknown until key is created.
- Is PHP core covered by OSV.dev? Assumed no; use the cited local entry.
