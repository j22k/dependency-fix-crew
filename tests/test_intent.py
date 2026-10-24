from agents.intent import (
    extract_repo, is_approval, is_rejection, parse_llm_json, regex_intent,
)


def test_version_from_text():
    assert regex_intent("Am I affected by the PHP vulnerability? I run PHP 8.3.31") == ("version", "8.3.31")


def test_repo_from_url():
    assert regex_intent("scan https://github.com/j22k/dependency-fix-crew.git please") == (
        "repo", "j22k/dependency-fix-crew")


def test_repo_from_word():
    assert regex_intent("check repo acme/shop") == ("repo", "acme/shop")


def test_unknown():
    assert regex_intent("hello there") == ("unknown", "")


def test_llm_json_plain_and_fenced():
    assert parse_llm_json('{"kind": "version", "target": "8.3.31"}') == ("version", "8.3.31")
    assert parse_llm_json('```json\n{"kind": "repo", "target": "a/b"}\n```') == ("repo", "a/b")


def test_llm_json_unusable():
    assert parse_llm_json("") is None
    assert parse_llm_json("not json") is None
    assert parse_llm_json('{"kind": "unknown", "target": ""}') is None


def test_approval_and_rejection():
    assert is_approval("Yes") and is_approval("yes, file it") and is_approval("approve!")
    assert is_rejection("no") and is_rejection("cancel")
    assert not is_approval("maybe")


def test_extract_repo():
    assert extract_repo("yes file it in j22k/demo") == "j22k/demo"
    assert extract_repo("yes") == ""
