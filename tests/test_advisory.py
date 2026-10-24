
import asyncio
from unittest.mock import AsyncMock, patch

from agents.advisory import on_request
from agents.models import AdvisoryRequest, AdvisoryResult


def test_constraint_only_returns_could_not_verify():
    msg = AdvisoryRequest(
        session_id="test-session",
        php_constraint="^8.2",
        php_version="",
        packages={},
    )

    ctx = AsyncMock()

    asyncio.run(on_request(ctx, "test-sender", msg))

    ctx.send.assert_awaited_once()
    result = ctx.send.await_args.args[1]

    assert isinstance(result, AdvisoryResult)
    assert result.ok is False
    assert "Could not verify PHP core" in result.error

def test_php2shell_83_is_affected_and_fixed_in_836():
    from agents.advisory import check_php_version, load_advisories

    findings = check_php_version("8.3.31", load_advisories())

    php2shell = next(
        finding for finding in findings
        if finding.advisory_id == "PHP2Shell"
    )

    assert php2shell.affected is True
    assert php2shell.installed == "8.3.31"
    assert "8.3.36" in php2shell.fixed_in