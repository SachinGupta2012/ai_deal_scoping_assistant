"""FR-2 schemas — PRD + functional scope. Every capability refs >=1 reviewed req ID."""
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

from app.schemas.scope import ScopeObjective

ScopeKind = Literal["customer-requested", "AI-interpretation", "recommended-enhancement", "assumption-needs-confirmation", "out-of-scope"]

_PRD_TEXT_LISTS = ("personas", "journeys", "nfr_summary", "integrations", "dependencies", "assumptions", "risks", "out_of_scope", "open_questions")


class Capability(BaseModel):
    capability_id: str = Field(pattern=r"^CAP_[0-9]{2,}$")
    name: str = Field(min_length=3)
    description: str = Field(min_length=20)
    included_req_ids: List[str] = Field(min_length=1)
    priority: Literal["High", "Medium", "Low"] = "Medium"
    dependencies: List[str] = []
    scope_kind: ScopeKind = "customer-requested"


def _stringify(item) -> str:
    """Accept str or structured dict; always return an informative narrative string."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("name", "question", "risk", "description", "role"):
            val = item.get(key)
            if isinstance(val, str) and val:
                extras = [f"{k}: {v}" for k, v in item.items() if k != key and isinstance(v, (str, int, float, bool, list)) and v]
                return f"{val}" + (f" ({'; '.join(extras)})" if extras else "")
        parts = []
        for k, v in item.items():
            if isinstance(v, (str, int, float, bool)) and v != "":
                parts.append(f"{k}: {v}")
            elif isinstance(v, list) and v and all(isinstance(x, (str, int, float)) for x in v):
                parts.append(f"{k}: {', '.join(str(x) for x in v)}")
        return "; ".join(parts) if parts else str(item)
    return str(item)


class _StringListValidator:
    pass


class PRDModel(BaseModel):
    session_id: str
    overview: str = Field(min_length=20)
    business_problem: str = Field(min_length=20)
    objectives: List[ScopeObjective] = []
    personas: List[str] = []
    journeys: List[str] = []
    capabilities: List[Capability]
    nfr_summary: List[str] = []
    integrations: List[str] = []
    dependencies: List[str] = []
    assumptions: List[str] = []
    risks: List[str] = []
    out_of_scope: List[str] = []
    open_questions: List[str] = []
    provider: str = ""
    model: str = ""
    prompt_version: str = "prd_v1"
    scope_version_no: int = 0

    @model_validator(mode="before")
    @classmethod
    def _coerce_lists_and_objectives(cls, v):
        if isinstance(v, dict):
            v = dict(v)
            for field in _PRD_TEXT_LISTS:
                if isinstance(v.get(field), list):
                    v[field] = [_stringify(x) for x in v[field]]
            if isinstance(v.get("objectives"), list):
                objs = []
                for o in v["objectives"]:
                    objs.append(o if isinstance(o, (str, dict)) else {"description": str(o)})
                v["objectives"] = objs
        return v

    @model_validator(mode="after")
    def _normalize_objectives(self):
        self.objectives = [ScopeObjective.model_validate(o) for o in self.objectives]
        return self


class CoverageModel(BaseModel):
    session_id: str
    total_requirements: int
    covered_req_ids: List[str] = []
    uncovered_req_ids: List[str] = []
    unsupported_capabilities: List[str] = []
    unsupported_integrations: List[str] = []
    unsupported_ai_use_cases: List[str] = []
    coverage_pct: float = 0.0
