"""
backend/graph/nodes.py

Six node stub functions for the SevaMithra LangGraph orchestrator. Each is
a no-op placeholder: it mutates the parts of SevaState it will own for
real in Rungs 8-12, using hardcoded/deterministic values instead of real
agent logic, LLM calls, ChromaDB queries, or mock-API calls. Every node's
job here is just to prove the graph shape and the checkpointer round-trip
end-to-end.

NOTE on schema fidelity: SchemeThread.phase and SevaState.current_phase
are declared in backend/state.py as Literal enums that do not include
several of the stub-stage values used below ("matched", "documents_verified",
"submitted", "rti_drafted" for SchemeThread.phase; "monitor", "escalate" for
SevaState.current_phase — state.py instead has "monitoring"/"escalation").
Python does not enforce TypedDict Literals at runtime, and backend/state.py
is explicitly out of scope for this rung, so these stub values are written
as-is. A static type checker (mypy) would flag them. Reconciling this —
either by widening the Literals in state.py or remapping these stub values
to the existing enum members — is left to whichever of Rungs 8-10 first
replaces these stubs with real logic.
"""

from datetime import datetime, timezone

from backend.state import SevaState, make_reasoning_step, make_scheme_thread


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def trigger_node(state: SevaState) -> dict:
    raw_input = state["user_profile"]["raw_input"]
    step = make_reasoning_step(
        agent="trigger",
        action="parse_input",
        detail=(
            f"[STUB] Received raw user input ({len(raw_input)} chars) and did "
            "nothing further with it. Real Trigger node will call the LLM "
            "wrapper (backend.llm.chat_json) to extract a structured "
            "UserProfile from voice/text input."
        ),
    )
    return {
        "current_phase": "trigger",
        "reasoning_log": [step],
        "updated_at": _now_iso(),
    }


def discovery_node(state: SevaState) -> dict:
    scheme_id = "PM-KISAN"
    thread = make_scheme_thread(
        scheme_id=scheme_id,
        scheme_name="PM Kisan Samman Nidhi",
        confidence=0.85,
    )
    thread["phase"] = "matched"

    step = make_reasoning_step(
        agent="discovery",
        action="match_schemes",
        detail=(
            "[STUB] Hardcoded a single match: PM-KISAN, confidence 0.85, "
            "instead of actually searching. Real Discovery node will "
            "semantically query the ChromaDB scheme corpus "
            "(backend.ingestion.retrieve.query_schemes) against the user's "
            "profile and rank real candidates."
        ),
        scheme_id=scheme_id,
    )
    return {
        "current_phase": "discovery",
        "scheme_threads": {scheme_id: thread},
        "pursued_scheme_ids": [scheme_id],
        "reasoning_log": [step],
        "updated_at": _now_iso(),
    }


def verification_node(state: SevaState) -> dict:
    updated_threads = {}
    for scheme_id, thread in state["scheme_threads"].items():
        updated = dict(thread)
        updated["phase"] = "documents_verified"
        updated_threads[scheme_id] = updated

    step = make_reasoning_step(
        agent="verification",
        action="verify_documents",
        detail=(
            "[STUB] Marked every scheme thread as documents_verified without "
            "checking any actual document. Real Validator node will call the "
            "mock DigiLocker endpoint (backend.mocks.api) for each required "
            "document and branch on missing/expired/mismatched status."
        ),
    )
    return {
        "current_phase": "verification",
        "scheme_threads": updated_threads,
        "reasoning_log": [step],
        "updated_at": _now_iso(),
    }


def execution_node(state: SevaState) -> dict:
    updated_threads = {}
    for scheme_id, thread in state["scheme_threads"].items():
        updated = dict(thread)
        updated["phase"] = "submitted"
        updated["application_id"] = f"APP-{scheme_id}-STUB"
        updated_threads[scheme_id] = updated

    step = make_reasoning_step(
        agent="execution",
        action="submit_application",
        detail=(
            "[STUB] Assigned a fake application_id to every scheme thread "
            "without submitting anything. Real Filler node will assemble the "
            "application payload from the verified documents and POST it to "
            "the mock applications/submit endpoint (backend.mocks.api)."
        ),
    )
    return {
        "current_phase": "execution",
        "scheme_threads": updated_threads,
        "reasoning_log": [step],
        "updated_at": _now_iso(),
    }


def monitor_node(state: SevaState) -> dict:
    now = _now_iso()
    updated_threads = {}
    for scheme_id, thread in state["scheme_threads"].items():
        updated = dict(thread)
        updated["phase"] = "monitoring"
        # SevaState has no top-level "monitor_started_at" field, and
        # backend/state.py is out of scope for this rung, so the start
        # timestamp is recorded on the already-declared per-thread field
        # closest in meaning: last_status_check_at.
        updated["last_status_check_at"] = now
        updated_threads[scheme_id] = updated

    step = make_reasoning_step(
        agent="monitor",
        action="begin_monitoring",
        detail=(
            "[STUB] Flagged every scheme thread as monitoring and stamped "
            "last_status_check_at. Does NOT actually wait. Real Monitor Agent "
            "(Rung 10) uses the SqliteSaver checkpointer to pause the graph, "
            "sleep past the Citizen Charter deadline, wake up autonomously, "
            "and check status via the mock applications/status endpoint."
        ),
    )
    return {
        "current_phase": "monitor",
        "scheme_threads": updated_threads,
        "reasoning_log": [step],
        "updated_at": now,
    }


def escalate_node(state: SevaState) -> dict:
    updated_threads = {}
    for scheme_id, thread in state["scheme_threads"].items():
        updated = dict(thread)
        updated["phase"] = "rti_drafted"
        # Rung 6 spec calls this field "rti_markdown"; backend/state.py's
        # SchemeThread already declares "rti_draft" for this purpose, so
        # that existing field is used rather than adding an undeclared key.
        updated["rti_draft"] = "[stub RTI content]"
        updated_threads[scheme_id] = updated

    step = make_reasoning_step(
        agent="escalate",
        action="draft_rti",
        detail=(
            "[STUB] Wrote placeholder text into rti_draft for every scheme "
            "thread instead of drafting anything real. Real Escalation node "
            "will call backend.rti.renderer to produce a filing-ready Tier-1 "
            "grievance email and Tier-2 RTI application from the verified "
            "clause corpus in backend/rti/clauses.json."
        ),
    )
    return {
        "current_phase": "escalate",
        "scheme_threads": updated_threads,
        "reasoning_log": [step],
        "updated_at": _now_iso(),
    }
