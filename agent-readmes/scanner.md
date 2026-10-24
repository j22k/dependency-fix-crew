![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

# Dependency Fix Crew: Scanner

**Address:** `TODO agent1q... (fill in after the Scanner first runs)`

Worker agent of the Dependency Fix Crew. Given a PHP version string or a GitHub repo, it
determines what the user runs by reading the repo's `composer.json` / `composer.lock` through the
GitHub API. It reports where the version came from and never guesses; if it only finds a
version constraint it says so.

Normally called by the Concierge agent, not directly by users.
Repo: https://github.com/j22k/dependency-fix-crew
