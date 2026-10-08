# Phase Gap Tracker

> Purpose: record every honest gap found during per-phase PRD verification.
> When all phases complete, revisit each item and close or carry forward.
> Format per gap: [OPEN / CLOSED] — description — where it will be resolved.

## Phase 1 — Scope + Foundation
- [OPEN] No live end-to-end click-through run yet (unit + contract tested only) — resolve in final integration pass.
- [OPEN] `recommend_platform` not part of Phase 1 (moved to Phase 3) — n/a, delivered in Phase 3.

## Phase 2 — PRD + Functional Scope (FR-2)
- [OPEN] Only `capabilities` implemented; `Modules / Workstreams / Delivery packages` grouping missing — resolve in FR-5 estimation (workstream decomposition).
- [OPEN] No full reqs×capabilities matrix grid UI (cards + coverage line only) — resolve in polish / Final Package coverage view.
- [OPEN] No live end-to-end run (approve → generate with real AI) — resolve in final integration pass.

## Phase 3 — Cloud Architecture (FR-3)
- [OPEN] Mermaid stored + displayed as text only, not rendered as visual graph — resolve in polish (add mermaid renderer / ReactFlow).
- [OPEN] No live end-to-end run (approve → generate arch with real AI) — resolve in final integration pass.
- [OPEN] `recommend_platform` is a simple keyword rule; AI rationale layered on top — acceptable, revisit only if recommendation quality is poor in UAT.

## Phase 4 — Data / Integration / AI Strategy (FR-4)
- [CLOSED 2026-10-08] DataDomain explicit fields added: ingestion, storage_transactional, storage_analytical, metadata, reporting, backup_recovery (optional, backward-compatible) + prompt rules + frontend + tests.
- [CLOSED 2026-10-08] AIUseCase explicit fields added: model_options[], orchestration, prompt_management + prompt rules + frontend + tests.
- [CLOSED 2026-10-08] Coverage now spans capabilities + integrations + AI use cases (extended compute_coverage, per-category unsupported lists, stored + audited on data_ai.generate, shown in UI).
- [OPEN] data_flow_mermaid text-only, same renderer gap as Phase 3 — resolve in polish.
- [OPEN] No live end-to-end run (approve → generate data/AI with real AI) — resolve in final integration pass.

## Phase 5 — Estimation (FR-5)
- (pending)

## Phase 6 — Package / Change-Impact / Quality Gate (FR-6)
- (pending)

---
*Created 2026-10-08. Update on every phase verification.*
