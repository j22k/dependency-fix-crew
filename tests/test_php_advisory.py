
import json
from pathlib import Path

from agents.advisory import check_php_version

ADVISORIES_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "advisories.json"
)

with ADVISORIES_PATH.open(encoding="utf-8") as f:
    ADVISORIES = json.load(f)["advisories"]


def test_php2shell_version_boundaries():
    cases = [
        ("8.3.35", True),
        ("8.3.36", False),
        ("8.3.37", False),
        ("8.4.26", True),
        ("8.4.27", False),
        ("8.5.11", True),
        ("8.5.12", False),
        ("8.2.34", True),
        ("8.2.35", False),
    ]

    for version, expected_affected in cases:
        findings = check_php_version(version, ADVISORIES)

        assert len(findings) == 1
        assert findings[0].affected is expected_affected, (
            f"Unexpected result for PHP {version}"
        )


def test_current_legacy_branch_fallback():
    # Documents current implementation behavior, not
    # an independently verified security verdict.
    findings = check_php_version("8.1.33", ADVISORIES)

    assert findings[0].affected is True
