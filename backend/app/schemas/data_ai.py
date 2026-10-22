"""FR-4 schemas — data, integration, AI strategy. Every item refs >=1 reviewed req ID."""
import re
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

from app.schemas.normalize import remap_text


class DataDomain(BaseModel):
    domain_id: str = Field(pattern=r"^DD_[0-9]{2,}$")
    name: str = Field(min_length=3)
    sources: List[str] = Field(min_length=1)
    ownership: str = Field(min_length=3)
    ingestion: str = Field(default="")
    storage: str = Field(min_length=3)
    storage_transactional: str = Field(default="")
    storage_analytical: str = Field(default="")
    quality_rules: List[str] = []
    metadata: str = Field(default="")
    governance: str = Field(default="")
    retention: str = Field(default="")
    privacy: str = Field(default="")
    reporting: str = Field(default="")
    backup_recovery: str = Field(default="")
    related_req_ids: List[str] = Field(min_length=1)


class IntegrationItem(BaseModel):
    int_id: str = Field(pattern=r"^ITI_[0-9]{2,}$")
    name: str = Field(min_length=3)
    source_system: str = Field(min_length=2)
    target_system: str = Field(min_length=2)
    pattern: Literal["api-sync", "event", "batch", "file"] = "api-sync"
    auth: str = Field(default="")
    error_handling: str = Field(default="")
    retry: str = Field(default="")
    monitoring: str = Field(default="")
    sync_notes: str = Field(default="")
    related_req_ids: List[str] = Field(min_length=1)


class AIUseCase(BaseModel):
    uc_id: str = Field(pattern=r"^AI_[0-9]{2,}$")
    name: str = Field(min_length=3)
    problem: str = Field(min_length=10)
    ai_function: str = Field(min_length=10)
    deterministic_part: str = Field(default="")
    human_review: str = Field(min_length=5)
    framework: str = Field(min_length=3)
    framework_rationale: str = Field(min_length=10)
    model_options: List[str] = []
    orchestration: str = Field(default="")
    prompt_management: str = Field(default="")
    retrieval_needs: str = Field(default="")
    evaluation: str = Field(min_length=5)
    safety: str = Field(min_length=5)
    privacy: str = Field(default="")
    monitoring: str = Field(default="")
    related_req_ids: List[str] = Field(min_length=1)


class DataAIStrategyModel(BaseModel):
    session_id: str
    data_domains: List[DataDomain] = Field(min_length=1)
    integrations: List[IntegrationItem] = Field(min_length=1)
    ai_use_cases: List[AIUseCase] = Field(min_length=1)
    data_flow_mermaid: str = Field(min_length=20)
    provider: str = ""
    model: str = ""
    prompt_version: str = "data_ai_v1"
    scope_version_no: int = 0

    @model_validator(mode="before")
    @classmethod
    def _normalize_item_ids(cls, v):
        if isinstance(v, dict):
            keymaps = [
                ("data_domains", "DD", "domain_id", []),
                ("integrations", "ITI", "int_id", []),
                ("ai_use_cases", "AI", "uc_id", []),
            ]
            for field, prefix, key, _refs in keymaps:
                if isinstance(v.get(field), list) and all(isinstance(x, dict) for x in v[field]):
                    valid = re.compile(rf"^{prefix}_[0-9]{{2,}}$")
                    mapping = {}
                    for item in v[field]:
                        raw = str((item or {}).get(key, ""))
                        if raw and not valid.match(raw) and raw not in mapping:
                            mapping[raw] = None
                    for i, raw in enumerate(mapping, start=1):
                        mapping[raw] = f"{prefix}_{i:02d}"
                    if mapping:
                        for item in v[field]:
                            raw = str((item or {}).get(key, ""))
                            if raw in mapping:
                                item[key] = mapping[raw]
                                refs = item.get("related_req_ids")
                                if isinstance(refs, list):
                                    item["related_req_ids"] = [mapping.get(x, x) if not valid.match(str(x)) else x for x in refs]
                        if isinstance(v.get("data_flow_mermaid"), str):
                            v["data_flow_mermaid"] = remap_text(v["data_flow_mermaid"], mapping)
        return v
