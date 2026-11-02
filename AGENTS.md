# dsc26-swe-w04 (Nour transfers)

### Commands
- Tests: `pytest -q` (runs the suite in tests/; keep under 60 s)
- Install: `uv pip install -r requirements.txt` (pinned versions; do not change)
- Python: 3.12 via `uv venv --python 3.12`

### Conventions
- Test only through public interface: rules functions and HTTP API.
- Do not edit nour_transfers/ or contracts/; grader replaces them.
- Each test folder needs __init__.py; test file names must be unique.
- No skip/skipif/xfail (costs H00).
- Errors are application/problem+json with a problem type.

### Where things are
- Spec: SPEC.md (not in repo? provided by grader)
- Contract: contracts/transfer_card.schema.json
- Rules: nour_transfers/rules.py

### Known traps
- Inbox sorted by priority then request order, not request order alone.
- requestedAt is ISO 8601 UTC with trailing Z.
- CORS allows exactly two origins with credentials; never *.

### Before done
- `pytest -q` passes; no collection errors.
