from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PipelineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; owner: str; status: str; freshness_minutes: int; success_rate: float; last_run: datetime

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; pipeline_name: str; severity: str; category: str; title: str; root_cause: str; recommendation: str; confidence: float; status: str; created_at: datetime; resolved_at: datetime | None

class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; incident_id: int; action: str; actor: str; detail: str; created_at: datetime

class SimulateRequest(BaseModel):
    scenario: str = "schema_drift"

class ResolveRequest(BaseModel):
    actor: str = "portfolio-user"
