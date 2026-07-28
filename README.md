# mentor

An agent skill that refuses to let you ship code you can't explain.

Most "explain this code" skills are one-way: the agent talks, you nod, nothing sticks. This one runs a **comprehension loop** — it explains, then stops and makes you restate the reasoning in your own words, grades the restatement against the code, and tells you not to merge if you can't. It also keeps an append-only ledger of what you actually understand, so a year from now it knows which ideas you own and which you once got wrong.

It targets *comprehension debt*: code that ships without anyone able to defend it in review, debug it under pressure, or notice when the model was confidently wrong. The more of a codebase an agent writes, the faster that debt accrues.

## Install

```bash
git clone https://github.com/anek-dev/mentor-skill ~/.claude/skills/mentor
```

Any agent that discovers `<skills-root>/<name>/SKILL.md` works — Claude Code (`~/.claude/skills/`), Codex (`~/.codex/skills/`), and compatible runtimes.

### Optional: make it fire on its own

`SKILL.md` only runs when you invoke it. `ALWAYS-ON.md` in this repo makes the agent check every non-trivial diff by itself, look the concept up in your ledger, and start the loop when it finds something you don't own yet.

Append its contents to whichever file your agent always loads:

| runtime | file |
|---|---|
| omp | `~/.omp/agent/APPEND_SYSTEM.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` |
| Cursor | `.cursor/rules/mentor.mdc` |
| anything else | its always-loaded instruction file |

Two things to know before you do. It costs ~2 KB of context on **every** request, and it will interrupt you unprompted — that is the point, but it is also the reason people delete it. `skip mentor` drops it for one turn. The skill alone works fine without this file; add it once the loop has already earned its place in your day.

## Use

Say `mentor`, `teach me`, `explain this`, or `quiz me`. It also self-triggers right after non-trivial code is generated — concurrency, security, DB queries, algorithms, auth.

It deliberately stays quiet on CRUD, glue and styling. There's nothing to own there.

## What it actually does

**Explains in four beats** — and the order is the point:

1. **The concrete failure first.** A numbered timeline (`T0`, `T1`, …) with real state values and your real identifiers, ending in the user-visible damage. The bug class gets named *after* you've seen it, never before.
2. **The options, each with code.** Two to four real candidates including the naive one you'd have reached for. A table row can't teach a mechanism — nobody learns anything from the words "atomic CAS".
3. **The choice and its price.** Why this one wins *here*, plus what it costs: held resources, chosen timeouts, quiet assumptions. It also flags whether an alternative is a **genuine tradeoff** or **strictly dominated** — same weakness plus extra problems, only looks simpler. That distinction is often the whole lesson.
4. **The names.** Recap only. If a term appears here for the first time, the earlier beats were written wrong.

**Then it stops** and asks you to restate the chain without looking. It won't continue until you answer.

**Then it grades you** — and when you're wrong it traces the broken mental model *forward* to what it made impossible ("you collapsed these two mechanisms, which is why the comparison question was unanswerable"). Diagnosing the cause beats correcting the fact.

**It verifies adversarially.** Enumerates the input/state variants the code must handle before you merge — that's where post-merge fix cascades come from. Greps the diff for placeholders standing in for logic (`SELECT FALSE AS has_feature` makes a flag dead for every row and nothing fails loudly). And it's told plainly that the model which wrote the code — including itself — can be confidently wrong.

**It gates the merge.** Can't restate the what and the why? Don't merge. Comprehension is the gate, not "tests pass".

## The knowledge ledger

`~/.mentor/knowledge.jsonl`, append-only, one concept per line.

```json
{"ts":"2026-01-15","concept":"PKCE","aliases":["code_verifier","S256"],
 "status":"owned","domain":"auth/oidc","taught_on":"backend/security/oidc.py:96-113",
 "restated":true,"verified":true,"review_after":"2026-04-15",
 "misconceptions":["thought the protection came from the string being unguessable"],
 "related":["state","nonce","hash"],"next":null}
```

| status | meaning |
|---|---|
| `seen` | explained; you did not restate it |
| `shaky` | restated with errors, or only after correction |
| `owned` | restated cleanly and unprompted, including the price |

Read at the start of each session: skips what you own, re-tests what's `shaky`, and grows outward along `related` edges instead of picking topics at random. It records **misconceptions even when you end up understanding** — so it can say "you made this same mistake six months ago", which lands harder than a fresh correction.

JSONL rather than JSON for a reason the skill itself will teach you: appending avoids the read-modify-write race that would let two sessions silently overwrite each other.

`owned` expires. Understanding decays, and a stale `owned` is worse than no record — it suppresses exactly the re-teaching that would fix it. Each one carries a `review_after` about 90 days out; past that date the next encounter opens with one verification question instead of silence. Pass and the clock resets, fail and it drops back to `shaky`.

Because the file is append-only a concept can appear many times. **The last line wins**; the earlier ones are its history — how an idea went from `shaky` to `owned`.

### On the skill teaching you something wrong

The model explaining the code is the model that wrote it. A wrong explanation you faithfully restate gets filed as `owned` and becomes confident, invisible misinformation — the worst thing this can produce.

Asking the same model twice does not help; it reproduces the same error and the agreement reads as evidence. So on security, money, data-integrity and concurrency the skill has to ground the claim somewhere else before recording it: run the code where the claim is executable, or dispatch a source-reading subagent to check the real library implementation or RFC and quote the line. Claims that were only recalled get `"verified": false`.

## Language rules

Two failure modes, both explicitly banned:

- **Too academic** — defining "advisory lock" via "row lock", a second unknown term to explain the first.
- **Too dumbed-down** — a cute analogy that drops the mechanism, the real names, the real numbers.

The rule is **formal term AND real-life analogy in the same breath**, every term defined inline at first use. If your spoken language differs from the code's, it keeps the English identifier and puts the plain meaning beside it — no invented calques.

## Design notes

- Rules are abstract; examples only calibrate. Naming one specific past mistake would teach the agent to *expect* that mistake instead of finding the one actually present.
- Tables compare properties of things already explained. They never introduce a mechanism.

## License

MIT
