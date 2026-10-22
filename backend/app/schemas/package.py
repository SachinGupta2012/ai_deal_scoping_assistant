"""FR-6 schemas — change impact, quality gate, and package export."""
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

Severity = Literal["blocker", "warning", "info"]
GateStatus = Literal["Pass", "Review Required", "Blocked"]


class ChangeImpactRequest(BaseModel):
    changed_req_ids: List[str] = []
    changed_assumption_ids: List[str] = []
    config_changes: Dict[str, Any] = {}


class ChangeImpactModel(BaseModel):
    session_id: str
    changed_req_ids: List[str] = []
    changed_assumption_ids: List[str] = []
    config_changes: Dict[str, Any] = {}
    affected_req_ids: List[str] = []
    unaffected_req_ids: List[str] = []
    affected_capability_ids: List[str] = []
    affected_component_ids: List[str] = []
    affected_data_domain_ids: List[str] = []
    affected_integration_ids: List[str] = []
    affected_ai_use_case_ids: List[str] = []
    affected_workstream_ids: List[str] = []
    affected_outputs: List[str] = []
    unaffected_outputs: List[str] = []
    reasoning: List[str] = []


class QualityIssue(BaseModel):
    issue_id: str = Field(pattern=r"^QG_[0-9]{2,}$")
    severity: Severity
    category: str
    message: str
    related_ids: List[str] = []


class QualityGateModel(BaseModel):
    session_id: str
    status: GateStatus
    coverage_pct: float = 0.0
    uncovered_req_ids: List[str] = []
    open_question_count: int = 0
    assumptions_needing_review: int = 0
    estimate_confidence: str = ""
    issues: List[QualityIssue] = []
    summary: str = ""


class PackageModel(BaseModel):
    session_id: str
    disclaimer: str
    markdown: str
    export_path: str
    quality_gate: QualityGateModel
    change_impact: ChangeImpactModel | None = None
