"""Phase 1 scope schemas — strict. Missing source/origin is rejected."""
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

Origin = Literal["customer-stated", "AI-inferred", "assumed"]
Priority = Literal["High", "Medium", "Low"]
ReqType = Literal["BR", "FR", "NFR", "INT", "DATA", "SEC", "CONST", "DEP", "RISK"]


class Requirement(BaseModel):
    req_id: str = Field(pattern=r"^(BR|FR|NFR|INT|DATA|SEC|CONST|DEP|RISK)_[0-9]{2,}$")
    type: ReqType
    description: str = Field(min_length=10)
    priority: Priority
    chunk_id: str = Field(min_length=1)
    quote: str = Field(min_length=10)
    origin: Origin
    dependencies: List[str] = []
    questions: List[str] = []


class Assumption(BaseModel):
    asm_id: str
    text: str = Field(min_length=10)
    related_req_ids: List[str] = []
    needs_review: bool = True


class ClarificationQuestion(BaseModel):
    q_id: str
    text: str = Field(min_length=10)
    related_req_ids: List[str] = []
    blocking: bool = False


class ScopeObjective(BaseModel):
    obj_id: str = ""
    description: str = ""

    @model_validator(mode="before")
    @classmethod
    def _accept_string_or_object(cls, v):
        if isinstance(v, str):
            return {"description": v}
        return v


class ScopeModel(BaseModel):
    session_id: str
    requirements: List[Requirement]
    assumptions: List[Assumption] = []
    questions: List[ClarificationQuestion] = []
    objectives: List[ScopeObjective] = []

    @model_validator(mode="after")
    def _normalize_objectives(self):
        normalized = []
        for o in self.objectives:
            normalized.append(ScopeObjective(obj_id=o.obj_id, description=o.description))
        self.objectives = normalized
        return self
    provider: str = ""
    model: str = ""
    prompt_version: str = "extract_v1"
    degraded: bool = False
