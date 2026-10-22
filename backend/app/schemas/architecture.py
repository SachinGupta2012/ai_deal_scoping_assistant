"""FR-3 schemas — cloud-specific architecture. Every component refs >=1 req/NFR/assumption."""
import re
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

from app.schemas.normalize import normalize_ids, remap_text

CloudPlatform = Literal["aws", "azure", "gcp"]

# Logical layers the architecture must cover
LAYER = Literal[
    "frontend", "backend", "api", "database", "storage", "iam",
    "messaging", "integration", "ai_ml", "observability", "security",
    "deployment", "environments", "availability", "backup_dr",
]


class ArchComponent(BaseModel):
    component_id: str = Field(pattern=r"^COMP_[0-9]{2,}$")
    name: str = Field(min_length=3)
    layer: LAYER
    cloud_service: str = Field(min_length=3)
    supported_req_ids: List[str] = Field(min_length=1)
    purpose: str = Field(min_length=10)
    rationale: str = Field(min_length=10)
    tradeoffs: str = Field(default="")
    dependencies: List[str] = []
    security: str = Field(default="")


class ArchitectureModel(BaseModel):
    session_id: str
    platform: CloudPlatform
    platform_rationale: str = Field(min_length=20)
    components: List[ArchComponent] = Field(min_length=5)
    mermaid: str = Field(min_length=20)
    provider: str = ""
    model: str = ""
    prompt_version: str = "arch_v1"
    scope_version_no: int = 0

    @model_validator(mode="before")
    @classmethod
    def _normalize_component_ids(cls, v):
        if isinstance(v, dict) and isinstance(v.get("components"), list) and all(isinstance(x, dict) for x in v["components"]):
            key = "component_id"
            valid = re.compile(r"^COMP_[0-9]{2,}$")
            mapping = {}
            for item in v["components"]:
                raw = str((item or {}).get(key, ""))
                if raw and not valid.match(raw) and raw not in mapping:
                    mapping[raw] = None
            for i, raw in enumerate(mapping, start=1):
                mapping[raw] = f"COMP_{i:02d}"
            if mapping:
                for item in v["components"]:
                    raw = str((item or {}).get(key, ""))
                    if raw in mapping:
                        item[key] = mapping[raw]
                        deps = item.get("dependencies")
                        if isinstance(deps, list):
                            item["dependencies"] = [mapping.get(x, x) if not valid.match(str(x)) else x for x in deps]
                if isinstance(v.get("mermaid"), str):
                    v["mermaid"] = remap_text(v["mermaid"], mapping)
        return v
