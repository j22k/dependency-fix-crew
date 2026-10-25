"""Pure helpers for the Concierge: intent parsing and approval detection (stdlib only, easy to test)."""
import json
import re
from typing import Optional, Tuple

INTENT_PROMPT = (
    "You extract intent for a vulnerability-check assistant. Reply with JSON only, no prose: "
    '{"kind": "version" | "repo" | "unknown", "target": "<php version like 8.3.31, or owner/name>"}. '
    'Use "version" when the user states a PHP version, "repo" when they give a GitHub repo or URL, '
    'otherwise "unknown" with an empty target.'
)

_VERSION_RE = re.compile(r"\b(\d+\.\d+(?:\.\d+)?)\b")
_REPO_URL_RE = re.compile(r"github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/\s?#]|$)", re.I)
_REPO_WORD_RE = re.compile(r"\brepo(?:sitory)?\s+([\w.-]+/[\w.-]+)", re.I)
_YES = {
    "yes", "y", "approve", "approved", "ok", "okay", "confirm", "file it",
    "go ahead", "sure", "file github issue", "file issue", "file an issue",
}
_NO = {"no", "n", "cancel", "reject", "stop", "skip", "not now", "dont file", "don't file"}


def regex_intent(text: str) -> Tuple[str, str]:
    """Deterministic fallback used when the LLM is unavailable or unsure."""
    m = _REPO_URL_RE.search(text)
    if m:
        return "repo", f"{m.group(1)}/{m.group(2)}"
    m = _REPO_WORD_RE.search(text)
    if m:
        return "repo", m.group(1)
    m = _VERSION_RE.search(text)
    if m:
        return "version", m.group(1)
    return "unknown", ""


def parse_llm_json(raw: str) -> Optional[Tuple[str, str]]:
    """Parse the model's JSON reply (tolerates code fences). None if unusable."""
    if not raw:
        return None
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.M).strip()
    try:
        data = json.loads(cleaned)
    except ValueError:
        return None
    kind = str(data.get("kind", "unknown")).lower()
    target = str(data.get("target", "")).strip()
    if kind not in ("version", "repo") or not target:
        return None
    return kind, target


def is_approval(text: str) -> bool:
    t = text.strip().lower().rstrip(".!")
    if "approve_issue" in t:
        return True
    if any(phrase in t for phrase in ("file github issue", "file issue", "file it", "go ahead", "approve", "confirm")):
        return True
    return t in _YES or t.startswith("yes")


def is_rejection(text: str) -> bool:
    t = text.strip().lower().rstrip(".!")
    if "reject_issue" in t:
        return True
    if any(phrase in t for phrase in ("not now", "cancel", "reject", "stop", "skip", "don't file", "dont file")):
        return True
    return t in _NO or t.startswith("no ") or t == "no"


def parse_selection(text: str) -> Optional[dict]:
    """A card click arrives as a JSON string like {"action": "approve_issue", ...}; else None."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    if isinstance(data, dict):
        if data.get("action") in ("approve_issue", "reject_issue"):
            return data
        sel = data.get("selection")
        if isinstance(sel, dict) and sel.get("action") in ("approve_issue", "reject_issue"):
            return sel
        if isinstance(sel, str):
            try:
                inner = json.loads(sel)
                if isinstance(inner, dict) and inner.get("action") in ("approve_issue", "reject_issue"):
                    return inner
            except ValueError:
                pass
    return None


def extract_repo(text: str) -> str:
    """Pull owner/name from free text (used when approval needs a repo to file into)."""
    kind, target = regex_intent(text)
    if kind == "repo":
        return target
    m = re.search(r"\b([\w-]+/[\w.-]+)\b", text)
    return m.group(1) if m else ""
