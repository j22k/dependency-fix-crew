"""Canned responses so each owner can develop before neighbouring agents exist (USE_MOCKS=1)."""
from agents.models import (
    AdvisoryRequest, AdvisoryResult, FixRequest, FixResult, Finding, ScanRequest, ScanResult,
)


def mock_scan(req: ScanRequest) -> ScanResult:
    return ScanResult(session_id=req.session_id, ok=True, php_version="8.3.31", source="mock")


def mock_advisory(req: AdvisoryRequest) -> AdvisoryResult:
    return AdvisoryResult(
        session_id=req.session_id,
        ok=True,
        findings=[
            Finding(
                advisory_id="PHP2Shell",
                component="php-core",
                severity="critical",
                affected=True,
                installed=req.php_version,
                fixed_in=["8.5.12", "8.4.27", "8.3.36", "8.2.35"],
                sources=["https://unit42.paloaltonetworks.com/cve-2026-109618-cve-2026-109619/"],
            )
        ],
    )


def mock_fix(req: FixRequest) -> FixResult:
    return FixResult(
        session_id=req.session_id,
        ok=True,
        plan_markdown="1. Upgrade PHP to 8.3.36.\n2. Redeploy.\n3. Review logs since Oct 17.",
        issue_url="https://github.com/example/repo/issues/1" if req.file_issue else "",
    )
