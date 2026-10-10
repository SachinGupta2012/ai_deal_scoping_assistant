"""FR-5 schemas — deterministic effort, timeline, and ROM commercials."""
from typing import List, Literal

from pydantic import BaseModel, Field

Complexity = Literal["Low", "Medium", "High"]
Confidence = Literal["High", "Medium", "Low"]


class RoleRate(BaseModel):
    role: str = Field(min_length=2)
    rate_per_week: float = Field(ge=0)


def default_rate_card() -> List[RoleRate]:
    return [
        RoleRate(role="Solution Architect", rate_per_week=6000),
        RoleRate(role="Product/BA", rate_per_week=4500),
        RoleRate(role="Frontend Engineer", rate_per_week=5000),
        RoleRate(role="Backend Engineer", rate_per_week=5200),
        RoleRate(role="Data/Integration Engineer", rate_per_week=5600),
        RoleRate(role="AI Engineer", rate_per_week=6000),
        RoleRate(role="QA Engineer", rate_per_week=4200),
        RoleRate(role="DevOps Engineer", rate_per_week=5500),
        RoleRate(role="Delivery Manager", rate_per_week=5000),
    ]


class EstimateConfig(BaseModel):
    currency: str = "USD"
    contingency_pct: float = Field(default=0.2, ge=0, le=1)
    productivity_factor: float = Field(default=1.0, gt=0, le=2)
    team_capacity_pw_per_week: float = Field(default=3.0, gt=0, le=20)
    role_rates: List[RoleRate] = Field(default_factory=default_rate_card)


class ComplexityProfile(BaseModel):
    capability_count: int = 0
    integration_count: int = 0
    data_domain_count: int = 0
    ai_use_case_count: int = 0
    nfr_count: int = 0
    security_req_count: int = 0
    high_priority_count: int = 0
    complexity_score: float = 0
    complexity_band: Complexity = "Low"


class RoleAllocation(BaseModel):
    role: str = Field(min_length=2)
    allocation_pct: float = Field(ge=0, le=1)


class WorkstreamEstimate(BaseModel):
    workstream_id: str = Field(pattern=r"^WS_[0-9]{2,}$")
    name: str = Field(min_length=3)
    related_req_ids: List[str] = []
    complexity: Complexity
    effort_low_pw: float = Field(ge=0)
    effort_high_pw: float = Field(ge=0)
    timeline_low_weeks: float = Field(ge=0)
    timeline_high_weeks: float = Field(ge=0)
    blended_rate_per_week: float = Field(ge=0)
    roles: List[RoleAllocation]
    drivers: List[str] = []
    assumptions: List[str] = []
    dependencies: List[str] = []
    confidence: Confidence = "Medium"


class EstimationModel(BaseModel):
    session_id: str
    scope_version_no: int = 0
    config: EstimateConfig
    complexity: ComplexityProfile
    workstreams: List[WorkstreamEstimate] = Field(min_length=1)
    total_effort_low_pw: float = Field(ge=0)
    total_effort_high_pw: float = Field(ge=0)
    timeline_low_weeks: float = Field(ge=0)
    timeline_high_weeks: float = Field(ge=0)
    base_rom_low: float = Field(ge=0)
    base_rom_high: float = Field(ge=0)
    contingency_amount_low: float = Field(ge=0)
    contingency_amount_high: float = Field(ge=0)
    rom_low: float = Field(ge=0)
    rom_high: float = Field(ge=0)
    confidence: Confidence
    missing_inputs: List[str] = []
    risks: List[str] = []
    assumptions: List[str] = []
    calculation_rules: List[str] = []
    prompt_version: str = "estimate_v1"
