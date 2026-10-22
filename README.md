# AI Deal Scoping Assistant
[![CI/CD](https://github.com/SachinGupta2012/ai_deal_scoping_assistant/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/SachinGupta2012/ai_deal_scoping_assistant/actions/workflows/ci-cd.yml)

> **Source of Truth:** This README captures the full client requirements for building this project. Refer back here anytime during development.
> **Original Challenge Type:** AI Exponential League Rapid Application Development Challenge
> **Chosen Stack for this repo:** Backend `Python / FastAPI` + Frontend `Next.js + TypeScript`

---

## 1. What Is This Project?

Sales and delivery teams get messy customer inputs — RFPs, meeting notes, emails, discovery-call notes, partially structured docs.

Turning that into a proposal today is **manual, slow, and expert-dependent** (architects, BAs, delivery managers, SMEs).

**AI Deal Scoping Assistant** is a **browser-accessible, intelligent solution-consulting workspace** (NOT a generic chatbot, summarizer, or auto-quotation engine) that:

1. Takes unstructured customer requirements (text / markdown / PDF / DOCX / TXT)
2. Extracts a **structured, traceable, reviewable scope model**
3. Lets users **review/edit/approve** requirements, assumptions, constraints, questions
4. Generates **connected deliverables** grounded in that scope:
   - PRD + Functional Scope
   - Cloud-specific Solution Architecture + Diagram
   - Data + Integration + AI Strategy
   - Effort, Timeline, ROM Commercials (explainable/reproducible)
5. Supports **change-impact analysis** (change one requirement/assumption → see affected outputs)
6. Runs **coverage + consistency validation + quality gate**
7. **Exports an integrated scoping package** (Markdown / PDF / DOCX)

> Output is an **internal planning aid only**. Every export must contain:
> `This document is an AI-assisted internal planning output based on customer requirements and stated assumptions. It requires review and validation by qualified sales, architecture, delivery, security, and commercial stakeholders. It is not a final quote, contractual commitment, or delivery guarantee.`

### Target Users
1. **Sales / Presales** – initial opportunity understanding
2. **Solution Architects** – app, cloud, integration, data, security, AI design
3. **Delivery Managers** – approach, effort, timeline, risks, dependencies
4. **Product / BAs** – PRD, journeys, acceptance criteria
5. **Challenge / Engagement Managers** – Topcoder challenges / delivery packages / blended model

### Core User Journey (Must Implement)
1. Create new scoping session
2. Enter / paste / upload requirements
3. Review customer context + normalized requirements
4. Run AI-assisted analysis
5. Review structured reqs, source refs, constraints, assumptions, open questions
6. Edit / approve scope model
7. Generate PRD + functional scope
8. Select cloud (AWS / Azure / GCP) or request recommendation
9. Generate solution + data + integration + AI architecture
10. Review effort, timeline, assumptions, ROM commercials
11. Review coverage + consistency
12. Modify 1+ important requirement / assumption / config
13. Review affected outputs, regenerate / recalculate
14. Run final quality check
15. Export complete package

Use professional language: Understand need, Review scope, Clarify missing info, Approve requirements, Generate PRD, Design solution, Plan data flow, Select AI approach, Estimate delivery, Review change impact, Validate coverage, Prepare package.

---

## 2. Functional Requirements (Must Build All 6)

### FR-1: Customer Requirements Analysis
**Input:** plain text, markdown, RFP, discovery notes, business/tech reqs, existing-system info. Upload (PDF/DOCX/TXT) recommended but not mandatory.

**AI must extract:**
business objectives, users/personas, functional reqs, non-functional reqs, existing systems, integrations, data reqs, security/compliance, tech preferences, delivery constraints, dependencies, risks, missing info, assumptions, clarification questions.

**ID scheme (traceable):** `BR_01, FR_01, NFR_01, INT_01, DATA_01, SEC_01`, etc.

Each item must have: `id, type, description, priority, source_text/section, origin [customer-stated | AI-inferred | assumed], dependencies, open questions`.

UI must allow review + edit before downstream generation.

**Constraints:**
- Every req retains reference to originating customer text + origin classification.
- Missing/ambiguous critical info → surface as assumption / clarification question, NEVER silently invent.

### FR-2: PRD + Functional Scope Generation
PRD includes: overview, business problem, objectives, users/personas, journeys/workflows, functional reqs, NFRs, integrations, dependencies, assumptions, risks, out-of-scope, open questions, traceability.

Functional scope organized into: Capabilities / Modules / Workstreams / Delivery packages. Example:
```
Capability: Customer Onboarding
Included: FR_01, FR_02, INT_01
Scope: guided onboarding, ID verification, profile, CRM integration
Priority: High
Dependencies: IdP access, CRM API
```

Distinguish: customer-requested vs AI-interpretation vs recommended enhancement vs assumption-needs-confirmation vs out-of-scope.

Provide coverage view: which reqs covered by each capability.

**Constraints:**
- Every capability references >=1 reviewed requirement ID.
- Auto-identify uncovered reqs + unsupported additions (no manual diff needed).

### FR-3: Cloud Solution Architecture (AWS / Azure / GCP)
User selects cloud OR asks for recommendation.

Cover: frontend apps, backend services, APIs, DB/storage, IAM, messaging/events, integrations, AI/ML services, observability, security, deployment/runtime, envs (dev/test/prod), availability/scalability, backup/DR.

Map logical component → specific cloud service. Example:
```
Logical: Managed relational DB | Platform: Azure | Service: Azure Database for PostgreSQL
Supports: DATA_01, NFR_03, SEC_02
Rationale: managed PG, backups, encryption, regional HA
Assumption: ASM_04 PG approved
```
Must provide diagram / visual (use Mermaid / ReactFlow / draw.io-style).

Each component: name, cloud service, supported req IDs, purpose, rationale, trade-offs, dependencies, security.

**Constraints:**
- Must use platform-specific services, not generic tech list.
- Every major component references a req / NFR / security need / reviewed assumption.

### FR-4: Data, Integration, AI Strategy
**Data:** domains, sources, ownership, ingestion, transactional + analytical storage, quality, metadata/governance, retention, privacy/security, reporting/analytics, backup/recovery.

**Integration:** internal/external systems, APIs, events/messages, batch, file exchange, auth, error handling, retry, monitoring, sync considerations. Describe information flow.

**AI Approach:** use cases, AI-specific reqs, deterministic vs AI split, architecture pattern, model/provider options, RAG needs, agent/workflow orchestration, prompt + structured-output mgmt, evaluation, responsible-AI/safety, monitoring/feedback, human-review, privacy.

Recommend frameworks with rationale (e.g. LangChain, LangGraph, Semantic Kernel, Mastra, Vercel AI SDK, Spring AI, managed cloud AI, custom). Explain WHY, not just list. Separate AI functions vs deterministic rules vs mandatory human decisions.

**Constraints:**
- Every major integration + AI use case refs reviewed reqs + appears in design/coverage view.
- Recommendations include solution-specific rationale.

### FR-5: Effort, Timeline, Assumptions, ROM Commercials
Include: phases, workstreams, roles/skills, effort range, timeline range, milestones, dependencies, assumptions, risks, ROM range, confidence level.

Suggested phases: Discovery+Architecture, Experience+Core Platform, Data+Integration, AI Capabilities, Testing+Hardening, Deployment+Handover.

Configurable factors: capability count/complexity, integration count/complexity, infra complexity, data migration, AI complexity, security/compliance, testing, envs, team composition, role rates, productivity, contingency %, dependencies.

AI may suggest workstreams, complexity, roles, risks, explanations — BUT final numbers must come from **visible factors / documented calculation rules**, NOT unsupported LLM numbers. Example:
```
Workstream: Data+Integration | Reqs: DATA_01, INT_01, INT_02 | Complexity: High
Effort: 18-24 person-weeks | Drivers: 3 ext integrations, migration, validation...
Basis: Effort x blended rate + contingency | Confidence: Medium (API readiness unconfirmed)
```
If inputs missing: lower confidence, list missing info, show affected components, avoid false precision. Historical Topcoder data may be shown separately as context only.

**Constraints:**
- Effort/timeline/ROM reproducible from visible scope factors, rates, contingency, currency, rules.
- Missing inputs must reduce confidence or block calc, not silently default.

### FR-6: Integrated Scoping Package
Package contains: executive summary, objectives, req summary, PRD, functional scope, architecture + diagram, data + integration + AI approach, tech/frameworks, phases/workstreams, effort/timeline, ROM, assumptions, risks, dependencies, open questions, coverage, traceability.

**a) Change-Impact Handling (mandatory):** User can modify >=1 req / assumption / config (e.g. cloud, user volume, priority, deadline, integration complexity, security, AI provider, rate card, contingency, scope in/out). System must show affected vs unaffected. Example: `5k → 500k users` affects NFR_02/04, scalability, caching, DB sizing, perf testing, cost, effort, ROM; unaffected: personas, onboarding workflow, CRM integration. Allow regenerate/recalc affected only, preserve reviewed unaffected content.

**b) Quality Gate (before export):** Check coverage of high-priority reqs, uncovered reqs, unsupported additions, unjustified arch components, integrations missing from plan, AI use cases missing eval/privacy/safety/human-review, missing estimate inputs, unresolved questions, conflicting clouds/techs, estimate inconsistencies, assumptions needing validation. Example summary: `Coverage 92%, Uncovered 2, Open Q 4, Unsupported 1, Confidence Medium, Status: Review Required`.

Viewable + exportable (Markdown minimum, PDF/DOCX bonus). Must include disclaimer (see top).

**Constraints:**
- Modify >=1 req/assumption → see affected scope/arch/strategy/effort/commercials.
- Final package identifies uncovered, unresolved, unsupported, gaps, inconsistencies, needs-validation before export.

---

## 3. Solution Depth (Anti-Shallow Guardrails)
Must demonstrate ALL:
- Structured + reviewable scope model
- Source traceability at requirement level
- User review BEFORE downstream generation
- Multiple connected deliverables
- Requirement-to-output traceability
- Explainable + reproducible estimation
- Change-impact handling
- Coverage + consistency validation
- Pre-export quality gate

Single prompt-to-report FAILS even if report has all sections. Multiple prompts alone FAILS unless connected via shared reviewable scope model.

### Grounding Hierarchy
1. **Primary:** Customer requirements → PRD, scope, arch, data, integration, AI, plan, estimates, ROM
2. **Secondary:** User assumptions/config (cloud, volume, regions, deadlines, team, rates, security, contingency) — clearly identified
3. **Tertiary:** AI recommendations — clearly labeled + supported by reqs/rationale/constraints/assumptions/config. If insufficient info → clarification Q + assumption for review + lower confidence + mark requiring validation.

---

## 4. Recommended App Sections (UI Plan)
1. **Customer Requirements Workspace:** input/upload, opportunity context, normalized preview, scope model, source refs, assumptions, dependencies, missing info, questions, review/edit
2. **PRD + Scope Workspace:** objectives, personas, journeys, functional scope, NFRs, boundaries, enhancements, coverage
3. **Architecture Workspace:** cloud select, diagram, components, cloud services, security/deployment, rationale, trade-offs, traceability
4. **Data, Integration, AI Workspace:** domains/flows, integration inventory, data/integration diagram, AI use cases, AI arch, frameworks, eval, responsible-AI
5. **Estimate Workspace:** phases, workstreams, roles, complexity, effort range, timeline/milestones, rates, ROM, assumptions, confidence
6. **Final Package:** change-impact summary, coverage view, consistency checks, risks/questions, quality-gate, preview, export

Keep UI focused, clear, end-to-end — not overly enterprise-complex.

---

## 5. AI + Tech Expectations for THIS Repo

**AI functionality needed:** extraction, classification, missing-info detection, question generation, PRD gen, decomposition, arch recommendation, data/integration gen, AI use-case ID, framework rec, delivery plan gen, assumption/risk ID, change-impact explanation, package gen, consistency/coverage review.

**AI providers:** free-tier / local / open-source / mock / recorded samples / multi-agent / workflow / structured generation allowed. **Paid AI must NOT be required.** If live AI unavailable, full seeded demo must work in **clearly labeled mock mode** preserving same flow, scope model, traceability, PRD/arch structure, estimation, change-impact, validation, package gen. Validate structured AI outputs (e.g. Pydantic/Zod) before downstream use.

**Stack (locked for this repo):**
- Backend: `Python / FastAPI` — ingestion, orchestration, scope-model, PRD/scope gen, arch gen, data/integration/AI planners, estimation, traceability, change-impact, validation, export, mock provider
- Frontend: `Next.js + TypeScript` (App Router) — 6 workspaces above, review/edit flows, diagrams, coverage views, estimate configurators, quality gate, export
- Shared: JSON schemas (Pydantic + Zod mirror), seed content, tests
- Libs: Mermaid/ReactFlow for diagrams, Markdown/PDF/DOCX export, LangChain/LangGraph or custom orchestration (optional)

**Non-functional:** browser-accessible, runnable locally, responsive, no mandatory paid services, maintainable, documented, secure handling of customer reqs, transparent sources/assumptions/AI labels. Auth optional (if added, provide reviewer creds).

---

## 6. Deliverables Checklist
- [x] Working app (input → analysis → review → PRD/scope → arch+diagram → data/integration/AI → estimate/ROM → change-impact → coverage/consistency → package + mock mode)
- [x] Clean modular source (UI / ingestion / orchestration / scope-model / generators / estimation / traceability / change-impact / validation / export / mock)
- [x] Seed content: 4 scenarios (app-modernization, data/integration-heavy, AI-enabled, missing-info) + rates.json + schemas + doc structures
- [x] Automated tests: 36 passing (`backend/tests` — schema validation, traceability, coverage, unsupported-rec detection, effort calc, ROM calc, rate/contingency change, missing-input handling, change-impact, consistency, AI chain, mock mode)
- [x] This README (run locally, AI config, mock mode, processing flow, scope review, traceability, PRD/arch/data/AI gen, estimation/ROM, change-impact, validation, data protection, architecture/limitations)
- [x] Submission architecture diagram: [docs/architecture.md](docs/architecture.md)
- [ ] Demo video 3-5 min (input → review → approve → PRD → cloud select → arch → data/AI → estimate basis → coverage → change → quality check → export → mock mode) — remaining task

---

## 7. Evaluation Weight (Build Accordingly)
1. Req Analysis + Scope Model 20% | 2. PRD + Scope 15% | 3. Cloud Arch 15% | 4. Data/Integration/AI 15% | 5. Effort/Timeline/ROM 15% | 6. Change Impact + Quality 10% | 7. UX 5% | 8. Code Quality + Docs 5%

**Success = evaluator can:** open in browser → upload reqs → review reqs+sources → distinguish stated vs assumed → see missing info → edit/approve → get grounded PRD → see coverage → pick AWS/Azure/GCP → see cloud-specific arch → trace components → review data/integration/AI + rationale → understand estimate + reproduce ROM → see low-confidence areas → change 1 req/assumption → see impact → run coverage/consistency → review issues → export → run all in mock mode free.

---

## 8. How To Build This Project (Plan)

### Phase 0 — Scaffolding
```
ai_deal_scoping_assistant/
  backend/ (FastAPI) — app/main.py, routers/, services/, models/schemas.py, mock_provider/, estimation/, validation/, export/, tests/, seeds/
  frontend/ (Next.js TS) — app/(workspaces)/ requirements/ prd/ architecture/ data-ai/ estimate/ package/
  shared/ schemas.json
  seeds/ scenario_*.md + rates.json + mock_responses/
```

### Phase 1 — Scope Model (highest weight)
- Define Pydantic schemas: Requirement{id, type, description, priority, source_ref, origin, dependencies, questions}, Assumption, Question, ScopeModel
- Build ingestion: text paste + PDF/DOCX/TXT upload (backend: pypdf, python-docx)
- Mock AI extractor returning valid schema + 4 seeded scenarios
- Frontend review table: edit/approve, filter by type/origin, source highlight

### Phase 2 — PRD + Coverage
- Generator maps ScopeModel → PRD markdown (capabilities reference IDs)
- Coverage matrix component (reqs × capabilities), uncovered/unsupported detectors

### Phase 3 — Architecture + Data/AI
- Cloud catalog (AWS/Azure/GCP service maps) + recommender rule
- Diagram via Mermaid/ReactFlow, component cards with rationale/traceability
- Data/integration/AI planners with framework rationale + responsible-AI checklist

### Phase 4 — Estimation (must be reproducible)
- Deterministic calculator: `effort = f(capabilities, complexity, integrations, data, AI, NFRs)`, `ROM = effort × rates × (1+contingency)`, NO LLM numbers
- Config UI: rates, contingency, currency, productivity; confidence logic (missing inputs → lower/block)
- Unit tests for calc, rate change, missing inputs

### Phase 5 — Change-Impact + Quality Gate + Export
- Dependency graph: req → capabilities → arch → data/AI → workstreams → estimate
- On change: diff affected/unaffected, selective regenerate
- Quality checks engine (11 checks from FR-6b) + gate status
- Export Markdown (then PDF/DOCX) with mandatory disclaimer

### Phase 6 — Polish
- Mock-mode toggle, seed switcher, responsive styling, README run instructions, arch diagram, video

**Build order by scoring:** Scope (20%) → PRD (15%) + Arch (15%) + Data/AI (15%) + Estimate (15%) → Change/Quality (10%) → UX/docs (10%)

---

## 9. Local Run
```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Seed the owner account (dev-only: ENV=development + ALLOW_DEV_SEED_OWNER=true)
curl -s -X POST http://127.0.0.1:8000/auth/seed-owner \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@local.dev","password":"Owner123!","full_name":"Owner"}'

# Frontend
cd ../frontend
npm install
npm run dev                                        # http://localhost:3000
```

### Configuration (backend/.env — copy from .env.example)
```ini
ENV=development
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require

# AI modes:
#   Clearly-labeled mock mode (no keys, no paid services): USE_MOCK_AI=true, AI_PROVIDER=mock
#   Live single provider: USE_MOCK_AI=false, AI_PROVIDER=cloudflare|openrouter|groq|google
#   Live fallback chain:  USE_MOCK_AI=false, AI_PROVIDER=live_chain
AI_PROVIDER_CHAIN=cloudflare,openrouter,groq,google   # default; .env may reorder, e.g. google,groq,cloudflare,openrouter

# Provider keys (fill what you have)
GEMINI_API_KEY=            # gemini-3.8-flash
GROQ_API_KEY=              # openai/gpt-oss-120b
CLOUDFLARE_ACCOUNT_ID=     # CLOUDFLARE_MODEL=@cf/meta/llama-3.1-8b-instruct
CLOUDFLARE_API_TOKEN=
OPENROUTER_API_KEY=        # meta-llama/llama-3.3-70b-instruct:free

# Structured-output cache (dev only)
AI_CACHE_ENABLED=true
AI_CACHE_DIR=./storage/ai_cache
```
If every live provider is unreachable, the API fails loudly with a provider summary — it never silently fakes live output. Mock mode must be enabled explicitly and is clearly labeled in `/health` (`mock_mode=true`) and every response payload.

### Freemium Chain Rules
- `live_chain` walks `AI_PROVIDER_CHAIN` in order and uses the **first provider that returns a valid JSON payload** (some free providers still fail occasionally — chain fallback covers this).
- `AI_PROVIDER` values outside `mock | cloudflare | openrouter | groq | google | live_chain` fail at request time with the config error surfaced, not silently swapped.
- Structured-output cache: repeated identical runs hit `./storage/ai_cache` (key = prompt-version + payload hash + provider + model), returning the stored payload with `cache_hit: true` in the response trace.
- If all providers in the chain fail, the request fails loudly with the last provider error and provider trace.

### API Base (frontend)
- Default: `http://<hostname>:8000` — no `/api/v1` prefix; routers mount at root (`/sessions/...`, `/auth/...`).
- Override with `NEXT_PUBLIC_API_URL` (read in `frontend/lib/api.ts`). Default allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`.

### Current Backend Routes (verified list — 25 routes)
**Auth** — `POST /auth/seed-owner` (dev-only) · `POST /auth/login` · `GET /auth/me` · `GET /auth/users` (admin) · `POST /auth/users` (admin)

**Sessions + Requirements** — `POST /sessions` · `GET /sessions` · `POST /sessions/{sid}/ingest` (text + optional PDF/DOCX/TXT upload; pypdf/python-docx) · `POST /sessions/{sid}/analyze` (AI extraction → scope model) · `GET /sessions/{sid}/scope` · `PATCH /sessions/{sid}/scope/items` (meaning edits) · `POST /sessions/{sid}/approve` (409 conflict until scope reviewed; downstream generation requires approved scope)

**Deliverables (each: POST generate + GET read)** — `POST|GET /sessions/{sid}/prd` · `POST|GET /sessions/{sid}/architecture` (platform: `aws|azure|gcp` or `recommend`) · `POST|GET /sessions/{sid}/data-ai` · `POST|GET /sessions/{sid}/estimate` (body `{ "config": {...} }` or `{}`)

**FR-6 / Export** — `POST /sessions/{sid}/change-impact` · `POST|GET /sessions/{sid}/quality-gate` · `POST|GET /sessions/{sid}/package` (Markdown w/ mandatory disclaimer)

**Meta** — `GET /health` · `GET /openapi.json`

### Frontend pages
`/` (dashboard) · `/login` · `/sessions` (workspace list) · `/requirements/[id]` · `/prd/[id]` · `/architecture/[id]` · `/data-ai/[id]` · `/estimate/[id]` · `/package/[id]` · `/admin/users`

## 10b. CI/CD Pipeline (GitHub Actions)

Workflow: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) — runs on every push/PR targeting `main` (markdown-only changes skipped).

```
pull_request → main                 push → main
        │                                │
   [backend-check]  in parallel  [frontend-check]
    ruff (fatal rules) +           npm ci + tsc --noEmit
    pytest (postgres:16 svc)       + next build
        └────── needs both ────────┘
                       ▼
              [publish-images] (main push only)
              backend + frontend images → ghcr.io (tags: main, sha-<sha>)
                       ▼
              [deploy] — intentionally disabled stub
              (enable when a VPS/PaaS target exists)
```

Rules enforced by the pipeline:
1. **PRs to main** always run backend + frontend checks; failures block merge.
2. **Images publish only for reviewed main pushes** (`needs: [backend-check, frontend-check]`, PR event excluded).
3. Future deploy can only run after images publish — wire it to a GitHub environment with required reviewer approval for the "verify before deploy" gate.

### Branch protection to set (repo Settings → Branches → `main`)
- Require a pull request before merging
- Require status checks: `Backend (ruff + pytest)`, `Frontend (tsc + next build)`

### Local parity
`docker compose up --build` — spins Postgres + backend (:8000) + frontend (:3000) using the same images CI publishes.

## 11. Known Limitations / Notes
- Outputs are planning aids, not quotes/commitments — enforce disclaimer + human review.
- Customer data stored locally only in mock mode; live AI mode requires explicit provider configuration and customer approval.
- Estimation transparency > precision — always show drivers, rates, assumptions, confidence.
- Current export supports Markdown. PDF/DOCX export remains a bonus item.

---
*Last synced from client challenge brief on 2026-09-27. Keep this file as the build reference.*
