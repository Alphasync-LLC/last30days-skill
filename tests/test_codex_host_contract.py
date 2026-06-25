"""Host-contract tests for non-modal agent runtimes."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "skills" / "last30days" / "SKILL.md"


def _prose_flow() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    start_marker = "### Non-Modal Prose Flow"
    end_marker = "### Manual Setup Guide"
    start = text.find(start_marker)
    assert start != -1, f"missing section marker: {start_marker}"
    end = text.find(end_marker, start)
    assert end != -1, f"missing section marker: {end_marker}"
    return text[start:end]


def test_non_modal_hosts_are_named():
    prose = _prose_flow()
    for host in ("Codex", "Cursor", "Gemini CLI", "raw CLI"):
        assert host in prose


def test_non_modal_cookie_consent_uses_engine_allow_flag():
    prose = _prose_flow()
    consent = prose.index("Cookie consent")
    allow = prose.index("setup --allow-browser-cookies")
    decline = prose.index("FROM_BROWSER=off")
    assert consent < allow
    assert consent < decline


def test_non_modal_completion_mentions_safe_diagnose_and_project_trust():
    prose = _prose_flow()
    assert "safe `--diagnose`" in prose
    assert "LAST30DAYS_TRUST_PROJECT_CONFIG=1" in prose
    assert "Codex desktop" in prose
