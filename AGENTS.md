# dsc26-swe-w04 (Nour transfers): we write tests, not the service

### Commands
- Install: `uv pip install -r requirements.txt` (pinned versions; do not change)
- Python 3.12: `uv venv --python 3.12`
- All tests: `pytest -q` (whole suite must stay under 60 s)
- One test: `pytest -q tests/unit/test_rules.py::test_name`

### Where things are
- Spec: SPEC.md in repo root. Read it before writing any test.
- Contract schema: contracts/transfer_card.schema.json (read-only)
- Code under test, read-only: nour_transfers/rules.py, nour_transfers/app.py
- Our tests: tests/unit, tests/api, tests/contract; `client` fixture in tests/conftest.py

### Conventions
- Never edit nour_transfers/ or contracts/; the grader replaces them.
- Test only the public interface in SPEC.md: the three rules functions and the HTTP API.
  Never import private names or read/patch source; a rewrite with different internals is graded too.
- Expected values come from SPEC.md, never computed with the code under test.
- Each test folder needs __init__.py; test file names must be unique.
- No skip/skipif/xfail (fails the grader's clean-suite check).
- Errors are application/problem+json with a problem `type`.

### Known traps
- Test exact boundaries: cover exactly 3 and 7, stock left exactly equal to reserve, quantity 0 and 1.
- Zero sales: days_of_cover returns None, not 0.0.
- Assert the problem `type` (/problems/below-reserve vs /problems/not-pending), not only status 409.
- Inbox order is urgent, high, normal, then request order; request items out of priority order.
- requestedAt is ISO 8601 UTC with trailing Z; JSON keys are camelCase.
- CORS allows exactly https://branch.nour.example and http://localhost:5173 with credentials; never *.
- After approval, assert both branches' stock, and that a second approve is 409.

### Before done
- `pytest -q` passes with no collection errors or skips; new tests would fail if their rule broke.