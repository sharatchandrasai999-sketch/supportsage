# SupportSage

Rule-based customer support ticket triage from the command line.

**Honest note:** there is no LLM here. Classification, priority, and draft
replies are deterministic keyword rules, and every output row says so in its
`triage_note` field ("mock rule-based triage, no LLM call"). No API keys are
needed. It is a small, inspectable starting point for a real triage pipeline,
not a production support tool.

## What it does

- Classifies each ticket as `billing`, `technical`, `account`, or `other`
  using keyword rules.
- Assigns a priority: `high` for urgent words (urgent, asap, outage, data
  loss, charged twice, …) or a technical ticket mentioning a crash/outage;
  `medium` for billing or account; `low` otherwise.
- Drafts a short templated reply (2–3 sentences) per category, referencing
  the ticket subject and giving a next step. It is labelled a draft — a
  human should review it before sending.

## Install

```bash
pip install -e .
```

## Usage

```bash
supportsage triage examples/tickets.jsonl --out triaged.jsonl
```

Input is JSONL, one ticket per line:

```json
{"id": 1, "subject": "Charged twice", "body": "I was charged twice this month."}
```

Output is JSONL with the original fields plus `category`, `priority`,
`draft_reply`, and `triage_note`.

## Example output

```
triaged 6 tickets | categories: account=1, billing=2, other=1, technical=2 | priorities: high=3, low=2, medium=1
```

```json
{"id": 1, "subject": "Charged twice for my subscription", "body": "...", "category": "billing", "priority": "high", "draft_reply": "Thanks for writing about 'Charged twice for my subscription' — this looks like a billing question, so I've flagged it for the billing team. As a next step, please reply with the invoice number or the last four digits of the card used and we'll check the charge for you.", "triage_note": "mock rule-based triage, no LLM call"}
```

## Tests

```bash
python -m pytest
```
