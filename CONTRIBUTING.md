# Contributing

Thanks for helping. Rule-based customer support ticket triage (deterministic mock, no LLM calls). This is a small, personal project, so keep changes small and easy to review.

## Before you send a change

- Run the tests from any folder: `pytest -q` (tests must not depend on the current working directory)
- Keep the offline path working: triage must run on a local tickets file, no API key and no download.
- If you add a triage rule, ship a sample ticket that exercises it.

## Reporting a problem

Open an issue and include:

- The exact command you ran
- The input file, if it is about one
- What happened, and what you expected instead

Do not include API keys, private documents, or personal details.
