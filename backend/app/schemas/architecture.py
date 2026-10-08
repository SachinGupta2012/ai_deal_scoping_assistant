"""FR-3 schemas — cloud-specific architecture. Every component refs >=1 req/NFR/assumption."""
from typing import List, Literal
from pydantic import BaseModel, Field

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
