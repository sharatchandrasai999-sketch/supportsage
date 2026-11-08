"""Tests for supportsage."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from supportsage.triage import classify, draft_reply, priority_for, triage_ticket

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "tickets.jsonl"


def test_billing_ticket_classified_billing():
    ticket = triage_ticket(
        {"id": 1, "subject": "Refund for invoice", "body": "I was charged twice, please refund the payment."}
    )
    assert ticket["category"] == "billing"


def test_technical_crash_ticket_gets_high_priority():
    ticket = triage_ticket(
        {"id": 2, "subject": "App crash", "body": "The app crashes every time I open it."}
    )
    assert ticket["category"] == "technical"
    assert ticket["priority"] == "high"


def test_account_ticket_classified_account():
    ticket = triage_ticket(
        {"id": 3, "subject": "Can't log in", "body": "I forgot my password and the reset link isn't working."}
    )
    assert ticket["category"] == "account"
    assert ticket["priority"] == "medium"


def test_unknown_content_falls_to_other_low():
    ticket = triage_ticket(
        {"id": 4, "subject": "Just saying hi", "body": "Love the product, keep up the good work!"}
    )
    assert ticket["category"] == "other"
    assert ticket["priority"] == "low"


def test_draft_reply_references_subject_and_is_a_draft():
    ticket = triage_ticket(
        {"id": 5, "subject": "Invoice question", "body": "What is this price on my invoice?"}
    )
    assert "Invoice question" in ticket["draft_reply"]
    assert ticket["triage_note"] == "mock rule-based triage, no LLM call"
    assert len(ticket["draft_reply"].split(". ")) >= 2


def test_classify_and_priority_helpers():
    assert classify("my invoice price is wrong") == "billing"
    assert classify("nothing matches here") == "other"
    assert priority_for("billing", "invoice question") == "medium"
    assert priority_for("other", "urgent help needed") == "high"
    assert "subject" in draft_reply("other", "hello").lower() or "hello" in draft_reply("other", "hello")


def test_cli_end_to_end_on_sample_file(tmp_path):
    out = tmp_path / "triaged.jsonl"
    result = subprocess.run(
        [sys.executable, "-m", "supportsage", "triage", str(EXAMPLES), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    assert len(lines) == 6
    for row in lines:
        assert {"id", "subject", "body", "category", "priority", "draft_reply", "triage_note"} <= row.keys()
    categories = {row["category"] for row in lines}
    assert {"billing", "technical", "account", "other"} <= categories
    assert "triaged 6 tickets" in result.stdout


def test_cli_missing_input_file_errors_cleanly(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "supportsage",
            "triage",
            str(tmp_path / "nope.jsonl"),
            "--out",
            str(tmp_path / "out.jsonl"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr
