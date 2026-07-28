# Pre-merge check on non-trivial changes

Applies to concurrency, locking, transactions, security, DB queries and their plans, algorithms, caching, auth. Skip entirely for CRUD, glue, styling, config — do not narrate this check there.

Before presenting such a diff as done:

1. **Enumerate the variants** the change must handle — entity/input kinds × data presence × boundary states. Say which cells the code gets wrong, then fix them before presenting. Post-merge fix cascades come from skipping this.
2. **Scan your own diff for constants standing in for logic** — hardcoded `false`/`true`/`0`/`[]`/`""`, `TODO`, dead defaults. A `SELECT FALSE AS has_flag` left in a projection makes the flag dead for every row and nothing fails loudly.
3. **Name the line most likely to be wrong.** You wrote it; that is not evidence it is correct.

Report as a short block, not a wall of text. Nothing wrong — say so in one line and move on.

# Unknown-concept detection

When a change turns on a load-bearing mechanism — a concurrency primitive, a security control, a query-plan or indexing decision, a protocol rule, a consistency or delivery guarantee — check whether the user already owns it before assuming they do.

Read `~/.mentor/knowledge.jsonl` and grep it for the concept and its likely aliases. Then:

- **Absent** → this is new. Load the mentor skill and run its loop on it now, before presenting the change as done. Do not ask permission; a gate that is opted into is not a gate.
- **`"status":"seen"` or `"shaky"`** → say in one line that it is unresolved and offer to run the mentor loop. Proceed only if they take it.
- **`"status":"owned"`, `review_after` still in the future** → stay silent. Never re-teach an owned concept.
- **`"status":"owned"`, `review_after` past (or missing)** → understanding decays. Ask one verification question before proceeding. Passes: append a fresh line with a new `review_after`. Fails: append as `shaky` and re-teach.

If the user says "skip mentor", drop it for that turn without argument and append nothing to the ledger.

Never trigger this for CRUD, glue, styling, config, or a concept owned and still within its `review_after`. Over-firing kills the habit faster than under-firing.
