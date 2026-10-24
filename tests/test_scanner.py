
from unittest.mock import Mock, patch

import pytest

from agents.scanner import exact_php_version, read_github_text


def test_exact_php_version():
    assert exact_php_version("8.3.31") == "8.3.31"
    assert exact_php_version("v8.3.31") == "8.3.31"
    assert exact_php_version("8.3") is None
    assert exact_php_version("^8.3") is None


@patch("agents.scanner.fetch_github_file")
def test_read_github_text(mock_fetch):
    import base64

    mock_fetch.return_value = {
        "content": base64.b64encode(b'{"require": {"php": "8.3.31"}}').decode()
    }

    result = read_github_text("owner", "repo", "composer.json")

    assert result == '{"require": {"php": "8.3.31"}}'
    mock_fetch.assert_called_once_with("owner", "repo", "composer.json")
