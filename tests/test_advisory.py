
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

