![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

# Dependency Fix Crew: Advisory

**Address:** `TODO agent1q... (fill in after the Advisory agent first runs)`

Worker agent of the Dependency Fix Crew. Matches a PHP version and Composer packages against
known advisories (a cited local advisory file for PHP core, OSV.dev for packages) and returns
affected or not, severity, fixed versions and sources. If a lookup fails it returns an error so
the crew says "could not verify" instead of "safe".

Normally called by the Concierge agent, not directly by users.
Repo: https://github.com/j22k/dependency-fix-crew
