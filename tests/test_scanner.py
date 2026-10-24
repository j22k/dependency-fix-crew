
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
    
    

from requests.exceptions import ConnectionError


@patch("agents.scanner.requests.get")
def test_fetch_github_file_retries_after_connection_error(mock_get):
    from agents.scanner import fetch_github_file

    mock_get.side_effect = [
        ConnectionError("Temporary network failure"),
        Mock(status_code=200, json=lambda: {"content": "e30="}),
    ]

    result = fetch_github_file("owner", "repo", "composer.json")

    assert result == {"content": "e30="}
    assert mock_get.call_count == 2



@patch("agents.scanner.requests.get")
def test_fetch_github_file_uses_timeout(mock_get):
    from agents.scanner import fetch_github_file

    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {"content": "e30="},
    )

    fetch_github_file("owner", "repo", "composer.json")

    assert mock_get.call_args.kwargs["timeout"] == 10



from requests.exceptions import ConnectionError


@patch("agents.scanner.requests.get")
def test_fetch_github_file_fails_after_two_attempts(mock_get):
    from agents.scanner import fetch_github_file

    mock_get.side_effect = ConnectionError("Network unavailable")

    with pytest.raises(ConnectionError):
        fetch_github_file("owner", "repo", "composer.json")

    assert mock_get.call_count == 2

