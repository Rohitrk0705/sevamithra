# backend/graph — LangGraph orchestrator skeleton

## What this is

The full 6-node SevaMithra state machine, wired end-to-end and checkpointed
via `SqliteSaver`. Every node is currently a **stub**: hardcoded/deterministic
output instead of real agent logic, no LLM calls, no ChromaDB queries, no
mock-API calls. The point of this rung is to prove the graph shape and the
checkpointer round-trip work today — real behavior gets bolted into these
stubs incrementally.

## Graph shape

```
START
  |
  v
trigger
  |
  v
discovery
  |
  +--(should_verify)--> [no matches] --> END
  |
  v  [has matches]
verification
  |
  v
execution
  |
  v
monitor
  |
  +--(should_escalate)--> [stub: always "escalate"] --> escalate --> END
```

## Which rung replaces which stub

| Node | Real logic lands in |
|---|---|
| `discovery_node` | Rung 8 — semantic ChromaDB query via `backend.ingestion.retrieve` |
| `verification_node`, `execution_node` | Rung 9 — real DigiLocker/application calls via `backend.mocks.api` |
| `monitor_node`, `escalate_node` | Rung 10 — real pause/wake via the checkpointer, RTI drafting via `backend.rti.renderer` |

**Monitor node in this rung does NOT wait. Real 60s pause + wake-up is Rung 10.**

## How to run

```bash
python -m backend.graph.run "farmer needs help"
```

Streams each node's reasoning step to the terminal as it runs (via
`graph.stream(..., stream_mode="updates")`), then prints the thread_id,
final phase, and every scheme thread's phase.

## Checkpoint storage

`backend/graph/checkpoints.sqlite` — a separate file from the toy
`checkpoints.sqlite` at the repo root created in Rung 2. It's gitignored:
it's a local, disposable SQLite file that regenerates on every run; there's
nothing in it worth versioning, and every thread_id gets its own row so
runs never collide.

## Known schema divergence (flagged, not fixed here)

`backend/state.py` was explicitly out of scope for this rung. Its declared
Literal enums don't cover every stub value used here:

- `SchemeThread.phase` (`SchemePhase` in state.py) doesn't include
  `"matched"`, `"documents_verified"`, `"submitted"`, or `"rti_drafted"` —
  the closest existing members are `"discovered"`, `"docs_ready"`,
  `"filed"`, `"escalated_rti"`.
- `SevaState.current_phase` doesn't include `"monitor"` or `"escalate"` —
  state.py has `"monitoring"` / `"escalation"` instead.

Python doesn't enforce TypedDict Literals at runtime, so none of this
breaks anything today, but a type checker would flag it. Whichever of
Rungs 8-10 first replaces these stubs with real logic should either widen
`state.py`'s Literals to match, or remap these stub values onto the
existing enum members.

Two field-name (not just value) mismatches were resolved by using the
already-declared field instead of inventing a new one: the escalate stub
writes to `rti_draft` (not `rti_markdown`, which doesn't exist), and the
monitor stub stamps `last_status_check_at` on each scheme thread instead of
a non-existent top-level `SevaState.monitor_started_at`.
