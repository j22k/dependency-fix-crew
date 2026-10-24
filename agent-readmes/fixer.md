![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

# Dependency Fix Crew: Fixer

**Address:** `TODO agent1q... (fill in after the Fixer first runs)`

Worker agent of the Dependency Fix Crew. Uses the ASI1 LLM to turn affected findings into a
remediation plan and a GitHub issue draft. It files the issue only after the user has approved
it in the chat, and returns the issue link.

Normally called by the Concierge agent, not directly by users.
Repo: https://github.com/j22k/dependency-fix-crew
