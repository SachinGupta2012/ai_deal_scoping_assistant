# Phase Gap Tracker

> Purpose: record every honest gap found during per-phase PRD verification.
> When all phases complete, revisit each item and close or carry forward.
> Format per gap: [OPEN / CLOSED] — description — where it will be resolved.

## Phase 1 — Scope + Foundation
- [CLOSED 2026-10-10] Mock mode now defaults to deterministic seeded generation with no paid AI required.
- [CLOSED 2026-10-10] Live AI chain added for Cloudflare Workers AI, OpenRouter, Groq, and Gemini with cache-backed fallback.
- [OPEN] No browser click-through run yet — backend tests and frontend TypeScript validation pass, but no manual/dev-server UI pass has been completed.
- [CLOSED 2026-10-10] `recommend_platform` delivered in Phase 3.

## Phase 2 — PRD + Functional Scope (FR-2)
- [CLOSED 2026-10-10] Workstream decomposition delivered in estimation.
- [CLOSED 2026-10-10] Reqs×capabilities matrix added to PRD workspace.
- [CLOSED 2026-10-22] Live-provider e2e run completed via script `e2e_run.ps1`: Gemini `gemini-3.8-flash` analyzed `scenario_missing_info.md` → 5 reqs (5/5 traceable, 3 blocking questions) → approved → PRD generated live (3 capabilities, coverage 60%, uncovered NFR_01/NFR_02 auto-detected).
## Phase 3 — Cloud Architecture (FR-3)
- [CLOSED 2026-10-10] Mermaid preview added as a dependency-free visual graph with raw Mermaid still shown.
- [CLOSED 2026-10-22] Live-provider e2e run completed: `POST /architecture` with Gemini returned AWS-locked design (8 components, 0 off-catalog, 0 missing layers, deterministic `identify_platform` fallback if catalog-only).
- [CLOSED 2026-10-10] `recommend_platform` upgraded to deterministic weighted scoring using cloud/ecosystem keywords from requirement text.

## Phase 4 — Data / Integration / AI Strategy (FR-4)
- [CLOSED 2026-10-08] DataDomain explicit fields added: ingestion, storage_transactional, storage_analytical, metadata, reporting, backup_recovery (optional, backward-compatible) + prompt rules + frontend + tests.
- [CLOSED 2026-10-08] AIUseCase explicit fields added: model_options[], orchestration, prompt_management + prompt rules + frontend + tests.
- [CLOSED 2026-10-08] Coverage now spans capabilities + integrations + AI use cases (extended compute_coverage, per-category unsupported lists, stored + audited on data_ai.generate, shown in UI).
- [CLOSED 2026-10-10] data_flow_mermaid preview added as a dependency-free visual graph with raw Mermaid still shown.
- [CLOSED 2026-10-22] Live-provider e2e run completed: `POST /data-ai` with Gemini returned 4 domains / 3 integrations / 1 AI use case with explicit domain fields + extended coverage 100%.

## Phase 5 — Estimation (FR-5)
- [CLOSED 2026-10-10] Deterministic estimation schemas/service/router added: workstreams, effort ranges, timeline ranges, role rates, productivity, contingency, ROM, confidence, missing inputs, calculation rules.
- [CLOSED 2026-10-10] Estimate workspace added with configurable currency, contingency, productivity, team capacity, ROM summary, workstream cards, missing inputs, and visible calculation rules.
- [CLOSED 2026-10-10] Unit coverage added for estimate generation, rate changes, contingency changes, and missing-input confidence reduction.
- [CLOSED 2026-10-10] `pytest` installed in `backend/.venv`; backend suite passing.
- [OPEN] No browser click-through run for estimate workspace yet — backend tests and frontend TypeScript validation pass, but no manual/dev-server UI pass has been completed.

## Phase 6 — Package / Change-Impact / Quality Gate (FR-6)
- [CLOSED 2026-10-10] Change-impact graph service/router/UI added for changed requirements, assumptions, and config changes.
- [CLOSED 2026-10-10] Quality gate service/router/UI added for coverage, unsupported outputs, architecture validation, AI governance, missing estimates, unresolved questions, and assumptions needing validation.
- [CLOSED 2026-10-10] Markdown package assembly/export added with mandatory disclaimer.
- [CLOSED 2026-10-10] Mock mode added across extraction, PRD, architecture, and data/AI generation.
- [CLOSED 2026-10-10] Seed set now includes app-modernization, data/integration-heavy, AI-enabled, missing-info, plus rates config.
- [CLOSED 2026-10-22] Backend test suite passes (`36 passed`) and frontend validation passes via `npm run lint` (`tsc --noEmit`).
- [OPEN] PDF/DOCX export not implemented — bonus only per README.
- [OPEN] Browser click-through/video not completed — requires manual/local UI pass.

---
*Created 2026-10-08. Update on every phase verification.*
