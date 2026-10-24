"""Team contract: typed messages between agents. Change only with all three owners' agreement."""
from typing import Dict, List

from uagents import Model


class ScanRequest(Model):
    session_id: str
    kind: str  # "repo" or "version"
    target: str  # repo URL (owner/name) or a PHP version string


class ScanResult(Model):
    session_id: str
    ok: bool
    error: str = ""
    php_version: str = ""
    packages: Dict[str, str] = {}  # composer package -> installed version
    source: str = ""  # where the data came from


class AdvisoryRequest(Model):
    session_id: str
    php_version: str
    packages: Dict[str, str] = {}


class Finding(Model):
    advisory_id: str
    component: str
    severity: str
    affected: bool
    installed: str
    fixed_in: List[str] = []
    sources: List[str] = []


class AdvisoryResult(Model):
    session_id: str
    ok: bool
    error: str = ""
    findings: List[Finding] = []


class FixRequest(Model):
    session_id: str
    target: str
    findings: List[Finding]
    file_issue: bool  # True only after explicit user approval


class FixResult(Model):
    session_id: str
    ok: bool
    error: str = ""
    plan_markdown: str = ""
    issue_url: str = ""
