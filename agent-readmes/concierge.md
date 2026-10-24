![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

# Dependency Fix Crew: Concierge

**Address:** `agent1qw8nlqj3xt3ejnhhcf2vmpk5d48sx6n2m4ekms2dd6pxzlg0vdpa7v6m9mg`

Ask this agent whether a known security vulnerability affects your software, and get a fix plan
and a GitHub issue. It is the entry point of a four-agent crew (Concierge, Scanner, Advisory,
Fixer) built for Fetch-A-Thon 3.0.

## Use it for
- "Am I affected by the PHP vulnerability from Oct 21? I run PHP 8.3.31"
- "Check my repo https://github.com/owner/name for the PHP vulnerability"

## What happens
1. Reads your request with the ASI1 LLM (PHP version or GitHub repo).
2. Scanner finds what you run, Advisory matches it to known advisories (PHP2Shell,
   CVE-2026-109618 / CVE-2026-109619, fixed in 8.5.12, 8.4.27, 8.3.36, 8.2.35).
3. Fixer drafts a remediation plan.
4. You get a review card (File GitHub issue / Not now). A GitHub issue is filed only after you
   approve.

If a check cannot be completed it says "could not verify" and never claims you are safe.

## Protocols
Agent Chat Protocol (ACP). Repo: https://github.com/j22k/dependency-fix-crew
