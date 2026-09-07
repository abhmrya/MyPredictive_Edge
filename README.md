# MyPredictive_Edge
# Predictive Edge Backend Architecture

This document explains the backend architecture of Predictive Edge in a practical, step-by-step way. It shows how the app is organized, how requests enter the system, how the backend validates and authorizes them, and how the API responds to the frontend.

---

## 1. Project overview

Predictive Edge is a full-stack platform for inventory routing and demand signal intelligence. The repository is organized as a monorepo:

- `apps/frontend` — React + TypeScript + Vite app
- `apps/backend` — Python FastAPI API server
- `supabase/` — database schema, migrations, and other Supabase assets
- `docs/` — technical documentation and planning notes

The backend is the core orchestration layer. It receives requests from the frontend, validates them, checks authorization, talks to Supabase for persistence and auth, and may trigger AI/optimization flows for routing decisions and demand intelligence.

---

## 2. Runtime technology stack

The backend is built with:

- Python 3.12+
- FastAPI for HTTP APIs
- Uvicorn as the ASGI server
- Supabase for authentication and database access
- Pydantic for schema validation and response models
- SlowAPI for request rate limiting
- Docker for local environment orchestration

This makes the backend fast, type-safe, and well-suited for a modular service that needs both web APIs and external integrations.

---

## 3. High-level architecture view

At a high level, the backend follows a layered architecture:

1. API layer
   - FastAPI app and route handlers
   - request validation
   - response serialization

2. Authorization layer
   - JWT verification using Supabase auth
   - RBAC checks like superadmin and executive access
   - permission-based gatekeeping

3. Service layer
   - business logic for onboarding, routing, invitations, users, chat, and alerts
   - orchestration with Supabase calls and external services

4. Data layer
   - Supabase Postgres tables
   - auth users and organization metadata
   - roles, permissions, invite flows, and generated records

5. Cross-cutting concerns
   - logging
   - request IDs and correlation IDs
   - CORS
   - exception handling
   - rate limiting

This is a clean backend pattern: route modules handle HTTP concerns, services handle business logic, and the data layer stores business state.

---

## 4. Main backend entry point

The main application is created in `apps/backend/app/main.py`.

This file does several important things:

- creates the FastAPI app
- sets up startup and shutdown hooks
- configures CORS
- adds middleware for logging and security headers
- registers exception handlers
- includes all API routers
- exposes the health endpoint

The key snippet is:

- `app = FastAPI(...)`
- `app.include_router(...)` for each module
- `@app.get("/api/health")` health check

This means the app is not a single giant file; it is a composition of modular route sets grouped by business domain.

---

## 5. Middleware and global behavior

The app includes global middleware that runs for every request.

### 5.1 Security headers middleware

This middleware adds headers such as:

- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Permissions-Policy`
- `Strict-Transport-Security` for HTTPS

This is important for hardening the API and reducing browser-side security risk.

### 5.2 Request logging middleware

This middleware does the following:

- reads or generates a request ID
- reads or generates a correlation ID
- captures the client IP
- stores the request metadata in request context
- measures duration of the request
- logs the request result
- adds `X-Request-ID` and `X-Correlation-ID` headers to the response

This helps with observability, debugging, and tracing a single call across services and logs.

### 5.3 CORS configuration

The app uses `CORSMiddleware` and allows configured origins from settings. This allows the frontend to call the API while restricting origins to approved values.

---

## 6. Exception handling strategy

The backend defines centralized exception handlers:

- `AppError` -> custom application error responses
- `RequestValidationError` -> structured validation errors for invalid request payloads
- `Exception` -> generic 500 fallback for unexpected server errors

This prevents route functions from leaking raw server errors and gives the client a consistent response format like:

```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    { "field": "org_name", "message": "Field required" }
  ]
}
```

This is a good pattern because frontend and API consumers can reliably handle failure states.

---

## 7. Router-based modular structure

The backend uses a feature-based module structure under `app/modules`.

Examples:

- `auth/` — onboarding, invite exchange, login flows
- `users/` — listing users, removing users, assigning roles
- `organizations/` — roles, permissions, invites
- `chat/` — LLM completion API
- `routing/` — decision approval and optimizer endpoints
- `signals/` — signals-related APIs
- `alerts/` — alerts-related APIs

Each module usually follows this structure:

- `routes.py` — HTTP endpoints
- `services.py` — logic and orchestration
- `schemas.py` — request/response models

This keeps endpoints thin and business logic reusable.

## Inventory and MCP integration

Inventory is organization-scoped and keyed by `(location_id, sku)`. Apply the
new migration before using the API:

```powershell
cd apps\backend
alembic upgrade head
```

The REST API uses the existing Supabase authentication and RBAC permissions:

- `GET /api/v1/inventory/organizations/{organization_id}`
- `GET /api/v1/inventory/organizations/{organization_id}/{inventory_id}`
- `PUT /api/v1/inventory/organizations/{organization_id}`
- `PATCH /api/v1/inventory/organizations/{organization_id}/{inventory_id}`

Install dependencies and run the MCP server over stdio for an MCP-compatible
client:

```powershell
pip install -r requirements.txt
python -m app.mcp.server
```

The MCP tools are read-only (`get_inventory` and `get_inventory_item`) and
reuse `SupabaseInventoryAdapter`, so MCP and REST cannot drift into separate
inventory implementations. Keep the MCP process in a trusted environment and
pass only organization IDs the caller is authorized to inspect.

For the Hindi/Hinglish MCP usage guide and database connection diagram, see
[`docs/mcp-guide-hi.md`](docs/mcp-guide-hi.md).

---

## 8. Real module example: auth

A strong example is the auth module.

### Route file

In `app/modules/auth/routes.py`, the auth endpoints are defined like:

- `POST /api/v1/auth/onboard`
- `GET /api/v1/auth/invite/exchange`
- `PATCH /api/v1/auth/invite/accept`
- `POST /api/v1/auth/demo-login`

These endpoints are thin wrappers. They validate input using schemas and then call service functions like:

- `onboard_organization(...)`
- `accept_invite(...)`
- `exchange_invite_token(...)`
- `demo_login(...)`

### Service file

The actual logic is implemented in `app/modules/auth/services.py`.

This file handles:

- validating org category values
- checking whether an account already exists
- creating an organization record in Supabase
- seeding default roles and permissions
- inviting a new admin via Supabase Auth
- creating the user row and linking it to org + role
- recording audit history

This separates HTTP concerns from core business rules.

---

## 9. Authorization and RBAC model

The project uses Supabase Auth plus role-based access control.

The main auth dependency is in `app/core/auth.py`.

### `get_current_user()`

This dependency:

1. reads JWT from the `Authorization: Bearer ...` header
2. calls `async_supabase.auth.get_user(...)`
3. looks up the user’s role and permissions
4. returns a user dictionary containing:
   - `user_id`
   - `role_name`
   - `permissions`
   - `organization_id`

### Role-based gate checks

The app defines dependencies like:

- `require_superadmin`
- `require_executive`
- `require_permission("manage_roles")`

This means some endpoints are only available to a restricted set of users. For example:

- executives can list users
- superadmins can assign roles or delete users
- certain permission-based routes require a specific permission key

This is central to the multi-tenant organization structure.

---

## 10. Supabase integration model

The backend talks to Supabase via the client wrappers in `app/services/supabase_client.py`.

It exposes:

- `SyncSupabase` for synchronous usage
- `AsyncSupabase` for async usage
- `async_supabase` proxy object used by the app

During app startup in `main.py`, the app initializes the async Supabase client via `AsyncSupabase.init()`.

This pattern matters because the backend keeps one shared client instance and avoids re-creating connections repeatedly.

Examples of Supabase usage:

- `async_supabase.table("organizations").insert(...)`
- `async_supabase.auth.admin.invite_user_by_email(...)`
- `async_supabase.auth.get_user(...)`
- `async_supabase.table("users").update(...)`

The database is not a custom service layer; it is the system of record via Supabase.

---

## 11. How a typical API request flows

Here is the full request lifecycle for a protected API call.

### Example: `GET /api/v1/users`

1. The frontend sends a request with a bearer token.
2. The request enters the FastAPI app in `app/main.py`.
3. `security_headers_middleware` runs and adds security headers.
4. `request_logging_middleware` generates and stores request IDs.
5. CORS middleware checks origins.
6. The request reaches the `list_users` route in `app/modules/users/routes.py`.
7. FastAPI validates query parameters and input models.
8. The route declares `Depends(require_executive)`.
9. `require_executive` calls `get_current_user()`.
10. `get_current_user()` validates the JWT using Supabase Auth.
11. It fetches role and org data from the app’s RBAC layer.
12. If the user is not authorized, it raises `ForbiddenError`.
13. If authorized, the route calls `fetch_users_in_org(...)` in the service layer.
14. The service queries Supabase for users in the current organization.
15. The response is serialized to a Pydantic model.
16. `X-Request-ID` and other headers are attached.
17. The client receives a structured JSON response.

This is the standard lifecycle for protected requests.

---

## 12. End-to-end request/response cycle for backend API

Below is a step-by-step flow for a typical backend request using the Predictive Edge API.

### Step 1: Request arrives at the app

The frontend or external client sends an HTTP request like:

```http
POST /api/v1/auth/onboard
Content-Type: application/json
Authorization: Bearer <token>
```

FastAPI receives it and matches the route path against registered routers.

### Step 2: Middlewares run first

Before route logic executes, the app runs its global middleware:

- security headers
- request logging
- CORS handling

This ensures observability and consistent platform behaviors for all requests.

### Step 3: Validation and dependency injection

FastAPI validates the incoming request body against the route schema.

For example, the auth onboarding route expects a payload like:

- organization name
- category
- admin name
- admin email
- maybe year of establishment

If the payload is malformed, the `RequestValidationError` handler returns a 422 JSON error.

### Step 4: Authorization checks run

If the endpoint is protected, FastAPI resolves dependencies such as `Depends(require_executive)` or `Depends(require_permission(...))`.

This usually calls Supabase Auth to verify the JWT and then checks the role and permission set.

### Step 5: Business logic executes in services

The route delegates to service functions like `onboard_organization`, `assign_user_role`, or `run_optimizer`.

This is where most of the app’s real behavior lives. Service functions perform:

- database checks
- multi-table Supabase operations
- role assignment
- orchestration with auxiliary services
- audit writing or event logging

### Step 6: Data layer interaction

The service talks to Supabase using `async_supabase`.

This may include:

- inserts into organizations
- selections from users
- role-permission seeds
- updates to invites
- admin operations for auth

### Step 7: Response built

Once the business logic completes, the service returns either a dictionary, a schema object, or a Pydantic response model.

FastAPI serializes that according to the route’s `response_model`.

### Step 8: Exception handling

If an error occurs, the app uses registered handlers to convert it into a clean JSON response instead of letting the app crash.

Typical responses include:

- `400` Bad Request
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `409` Conflict
- `422` Validation error
- `500` Internal error

### Step 9: Response returned to client

The final response contains:

- HTTP status code
- JSON payload
- request IDs in headers for traceability
- consistent error shape when applicable

This is the backend API response cycle in one sentence: request enters FastAPI -> middlewares -> validation/auth -> business logic -> DB -> serialization -> response.

---

## 13. Example: onboarding flow

The organization onboarding flow is a good example of the full architecture in action.

### Request

```http
POST /api/v1/auth/onboard
```

### Process

1. Client sends organization signup data
2. FastAPI validates payload against `OnboardRequest`
3. `onboard_organization(...)` runs
4. The service checks valid org category and uniqueness
5. It creates an organization row in Supabase
6. It seeds the default roles and permission sets
7. It invites the admin via Supabase Auth
8. It creates the base user profile and links them to org + role
9. It writes an audit event
10. It returns `OnboardResponse`

### Response

```json
{
  "org_id": "...",
  "user_id": "..."
}
```

This demonstrates how HTTP, business logic, auth, and database actions are coordinated in one call.

---

## 14. Example: protected organization route

For a route like `/api/v1/organizations/roles`, the flow is:

1. User sends authenticated request
2. `get_current_user` validates JWT
3. `require_permission("manage_roles")` checks permission
4. Service queries allowed organization roles
5. Response returns role list

This is how the access model enforces tenant scoped authorization outside the route itself.

---

## 15. Why this architecture works well

This project uses a familiar and scalable pattern:

- modular routes for maintainability
- thin route handlers
- dedicated service logic
- centralized auth and permissions
- Supabase as the source of truth
- consistent logging and exception handling
- clean separation of concerns

That gives the team a strong structure for future features like forecast signals, AI optimization, analytics, and additional domain modules.

---

## 16. Summary

The Predictive Edge backend is a FastAPI application structured around clear business modules and a shared service/data layer. Requests go through global middleware, validation, auth, business logic, and finally Supabase before a structured response returns to the client.

The most important architectural idea is this:

- HTTP entry points live in route modules
- business logic lives in service functions
- user identity and permissions are enforced centrally
- Supabase handles database and auth persistence
- global middleware keeps the app secure, observable, and consistent

This is a clean foundation for a growing AI-driven platform.
