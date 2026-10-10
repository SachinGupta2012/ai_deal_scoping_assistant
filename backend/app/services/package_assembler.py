"""Markdown package assembly and export."""
import os
from typing import Iterable

from app.schemas.package import ChangeImpactModel, PackageModel, QualityGateModel

DISCLAIMER = (
    "This document is an AI-assisted internal planning output based on customer requirements and stated assumptions. "
    "It requires review and validation by qualified sales, architecture, delivery, security, and commercial stakeholders. "
    "It is not a final quote, contractual commitment, or delivery guarantee."
)


def _lines(items: Iterable[str]) -> str:
    rows = [f"- {i}" for i in items if i]
    return "\n".join(rows) if rows else "- None"


def _req_summary(requirements: list[dict]) -> str:
    return "\n".join(f"- {r.get('req_id')} [{r.get('type')}/{r.get('priority')}/{r.get('origin', 'reviewed')}]: {r.get('description')}" for r in requirements) or "- None"


def assemble_markdown(session_id: str, scope: dict, gate: QualityGateModel, impact: ChangeImpactModel | None = None) -> str:
    prd = scope.get("prd") or {}
    arch = scope.get("architecture") or {}
    data_ai = scope.get("data_ai") or {}
    estimate = scope.get("estimate") or {}
    sections = [
        f"# AI Deal Scoping Package\n\n> {DISCLAIMER}",
        f"## Executive Summary\nSession: `{session_id}`\n\nQuality gate: **{gate.status}**. {gate.summary}",
        f"## Objectives\n{_lines(scope.get('objectives', []))}",
        f"## Reviewed Requirements\n{_req_summary(scope.get('requirements', []))}",
        f"## PRD + Functional Scope\nOverview: {prd.get('overview', 'Not generated')}\n\nCapabilities:\n" + _lines(f"{c.get('capability_id')} - {c.get('name')} ({', '.join(c.get('included_req_ids', []))})" for c in prd.get("capabilities", [])),
        f"## Architecture\nPlatform: {arch.get('platform', 'Not generated')}\n\nRationale: {arch.get('platform_rationale', '')}\n\nComponents:\n" + _lines(f"{c.get('component_id')} - {c.get('name')} / {c.get('cloud_service')} ({', '.join(c.get('supported_req_ids', []))})" for c in arch.get("components", [])) + f"\n\n```mermaid\n{arch.get('mermaid', '')}\n```",
        "## Data, Integration, and AI Strategy\nData domains:\n" + _lines(f"{d.get('domain_id')} - {d.get('name')} ({', '.join(d.get('related_req_ids', []))})" for d in data_ai.get("data_domains", [])) + "\n\nIntegrations:\n" + _lines(f"{i.get('int_id')} - {i.get('name')} ({', '.join(i.get('related_req_ids', []))})" for i in data_ai.get("integrations", [])) + "\n\nAI use cases:\n" + _lines(f"{a.get('uc_id')} - {a.get('name')} ({', '.join(a.get('related_req_ids', []))})" for a in data_ai.get("ai_use_cases", [])),
        f"## Effort, Timeline, and ROM\nEffort: {estimate.get('total_effort_low_pw', 'n/a')}-{estimate.get('total_effort_high_pw', 'n/a')} person-weeks\n\nTimeline: {estimate.get('timeline_low_weeks', 'n/a')}-{estimate.get('timeline_high_weeks', 'n/a')} weeks\n\nROM: {((estimate.get('config') or {}).get('currency') or '')} {estimate.get('rom_low', 'n/a')}-{estimate.get('rom_high', 'n/a')}\n\nConfidence: {estimate.get('confidence', 'n/a')}\n\nWorkstreams:\n" + _lines(f"{w.get('workstream_id')} - {w.get('name')}: {w.get('effort_low_pw')}-{w.get('effort_high_pw')} PW" for w in estimate.get("workstreams", [])),
        "## Assumptions, Risks, Dependencies, Questions\nAssumptions:\n" + _lines(a.get("text", "") for a in scope.get("assumptions", [])) + "\n\nRisks:\n" + _lines((prd.get("risks") or []) + (estimate.get("risks") or [])) + "\n\nOpen questions:\n" + _lines(q.get("text", "") for q in scope.get("questions", [])),
        "## Coverage and Quality Gate\n" + gate.summary + "\n\nIssues:\n" + _lines(f"{i.issue_id} [{i.severity}] {i.category}: {i.message} {' '.join(i.related_ids)}" for i in gate.issues),
    ]
    if impact:
        sections.append("## Change Impact\nAffected outputs: " + (", ".join(impact.affected_outputs) or "None") + "\n\nAffected requirements: " + (", ".join(impact.affected_req_ids) or "None") + "\n\nUnaffected requirements: " + (", ".join(impact.unaffected_req_ids) or "None"))
    return "\n\n".join(sections) + "\n"


def save_package(session_id: str, markdown: str, storage_dir: str = "storage") -> str:
    os.makedirs(storage_dir, exist_ok=True)
    path = os.path.join(storage_dir, f"{session_id}_scoping_package.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return path


def assemble_package(session_id: str, scope: dict, gate: QualityGateModel, impact: ChangeImpactModel | None = None) -> PackageModel:
    markdown = assemble_markdown(session_id, scope, gate, impact)
    path = save_package(session_id, markdown)
    return PackageModel(session_id=session_id, disclaimer=DISCLAIMER, markdown=markdown, export_path=path, quality_gate=gate, change_impact=impact)
