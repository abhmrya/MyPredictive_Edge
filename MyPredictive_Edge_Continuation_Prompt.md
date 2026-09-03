# MyPredictive_Edge — Continuation Prompt

Paste this at the start of any new chat/session to resume work on this project without re-explaining anything.

---

You are helping me build **MyPredictive_Edge**, a FastAPI + Supabase backend.

**Core business idea:** External signals → anomaly/shortage alert → optimizer → routing decision → human approval → inventory transfer.

## Non-negotiable working rules

1. **Understand first.** Before writing any code, explain what the module does, why it exists, and how it connects to the overall business flow.
2. **One step at a time.** Do not implement multiple modules together. Finish and test the current step before moving to the next.
3. **Reference architecture only.** I have a separate reference project. Use it only as an architectural guide — never copy its code, tables, fields, or auth assumptions blindly if they don't match my project.
4. **No blind copy-paste.** If reference code depends on tables/services I haven't built yet, tell me what's missing before writing anything.
5. **Test every module.** After implementation, give me a way to test it (API call, DB check, etc.) and confirm the result before continuing.
6. **Security by default.** Every module must consider authentication, RBAC, organization isolation, input validation, logging, and safe error handling.
7. **Human-in-the-loop.** Optimization only ever creates a *pending* decision. Inventory never moves until a human approves, rejects, or overrides it.
8. For each module, follow this exact sequence: **Why → Database design → Model → Schema → Service → Routes → RBAC → Test → Next module.**

## Current status

| Module | Status |
|---|---|
| FastAPI foundation | ✅ Done |
| Config (.env) | ✅ Done |
| Supabase client (sync/async) | ✅ Done |
| SQLAlchemy DB core | ✅ Done |
| Logging (request/correlation context) | ✅ Done |
| Middleware (security headers) | ✅ Done |
| Centralized exceptions | ✅ Done |
| Rate limiting (SlowAPI) | ✅ Done |
| Authentication (register/login/me/logout/refresh) | ✅ Done |
| Locations (table + CRUD + validation) | ✅ Done |
| **Organization management** | ⏳ **← We are here / NEXT** |
| RBAC (roles & permissions) | ⏳ Pending |
| Invitations | ⏳ Pending |
| Audit logging | ⏳ Pending |
| Inventory | ⏳ Pending |
| Signals & signal ingestion | ⏳ Pending |
| Anomaly alerts | ⏳ Pending |
| Warehouse tools | ⏳ Pending |
| LLM reasoning (MILPProblemSpec) | ⏳ Pending |
| MILP solver (PuLP) | ⏳ Pending |
| Optimizer pipeline | ⏳ Pending |
| Routing decisions | ⏳ Pending |
| Human approval workflow | ⏳ Pending |
| Inventory fulfillment/transfer | ⏳ Pending |
| Alert resolution | ⏳ Pending |
| End-to-end testing | ⏳ Pending |
| Production hardening | ⏳ Pending |

## Full phase roadmap (build order)

1. Organization Management — org model/schema/service/routes; connect users to organizations.
2. Roles & RBAC — `organization_roles`, `organization_role_permissions`; `require_permission(...)` dependency; RBAC caching.
3. Invitations — token, expiry, acceptance, role assignment, SendGrid email integration.
4. Audit Logging — record invitation, role change, optimization, approval, rejection, override, inventory movement; must never break the primary operation.
5. Inventory — `location_id`, `sku`, `stock_level`, `safety_stock_level`, timestamps, constraints, CRUD.
6. Signals & Signal Ingestion — adapters for weather/events/holidays/news/trends, run concurrently via `asyncio.gather`, `POST /api/v1/signals/ingest`.
7. Anomaly Alerts — `anomaly_alerts` schema/model/service; active/acknowledged/resolved states.
8. Warehouse Tools — controlled functions only: `get_open_alerts`, `get_inventory`, `get_locations`, `create_routing_decision`. No raw SQL access for the LLM.
9. LLM Reasoning — `MILPProblemSpec` (Pydantic), Groq tool-calling loop, validated structured JSON output.
10. MILP Solver — PuLP-based solver; hard constraints on source stock and destination capacity; solver (not LLM) owns feasibility.
11. Optimizer Pipeline — alert → LLM → warehouse tools → stock/capacity checks → solver → routing decision, with retry/self-correction on infeasibility.
12. Routing Decisions — `routing_decisions` schema/model/service/routes; `GET /decisions`, `POST /optimize`; store solver status, cost, quantity, notes.
13. Human Approval Workflow — approve/reject/override with RBAC; valid state transitions only (`PENDING → APPROVED/REJECTED`).
14. Inventory Fulfillment/Transfer — atomic source decrement + destination increment after approval, validated against stock/capacity.
15. Alert Resolution — resolve/acknowledge alerts tied to optimization/decision outcomes.
16. End-to-End Testing — auth, RBAC, org isolation, inventory, signals, alerts, optimizer feasibility, routing, approval flows, transfers; include failure/edge cases.
17. Production Hardening — secrets management, structured logging, timeouts, retries, idempotency, monitoring, API docs.

## Reference services available (architectural guides only, not final code)

- `signal_ingestion_service.py` — normalizes external signals into alert candidates.
- `warehouse_tools.py` — controlled optimizer/LLM data access layer.
- `llm_service.py` — LLM reasoning + `MILPProblemSpec` generation (Groq).
- `solver_service.py` — PuLP-based feasibility/quantity solver.
- `optimizer_pipeline.py` — orchestrates alert → LLM → tools → solver → routing decision, with retry loop.
- RBAC service — loads user org/role/permissions with TTL caching.
- Invite email service — SendGrid transactional invite emails.
- Audit service — writes `audit_log` records without breaking the primary operation.

## Business flow (for context)

```
External Signals → Signal Ingestion → Anomaly Detection → anomaly_alerts
   → Optimizer (LLM + Warehouse Tools + MILP Solver)
   → routing_decisions (PENDING)
   → Human (Approve / Reject / Override)
   → Inventory Fulfillment (source -qty, destination +qty)
   → Alert / decision lifecycle updated
```

## What I want from you right now

Start at **Phase 2 — Organization Management**. Follow the sequence in rule 8: explain the "why," propose the database design, then walk me through model → schema → service → routes → RBAC hook → test, one at a time, waiting for my confirmation between each before moving on. Do not jump ahead to later phases or bundle multiple modules together.
