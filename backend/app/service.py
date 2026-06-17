from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Pipeline, Incident, AuditEvent

SCENARIOS = {
    "schema_drift": {
        "pipeline": "payments_stream",
        "severity": "critical",
        "category": "Schema Drift",
        "title": "Unexpected string values detected in transaction_amount",
        "root_cause": "The upstream payment service changed transaction_amount from DECIMAL to VARCHAR. Twelve malformed records entered the stream after deployment v2.8.1.",
        "recommendation": "Quarantine malformed records, cast valid numeric strings, restore the producer schema contract, and replay the affected Kafka offsets.",
        "confidence": 0.96,
    },
    "freshness": {
        "pipeline": "customer_360_daily",
        "severity": "high",
        "category": "Freshness SLA",
        "title": "Gold customer table is 47 minutes stale",
        "root_cause": "The dbt customer merge waited on a locked dimension table after an overlapping backfill job started.",
        "recommendation": "Cancel the duplicate backfill, release the lock, rerun the merge task, and add a concurrency guard to the orchestration policy.",
        "confidence": 0.91,
    },
    "volume_anomaly": {
        "pipeline": "claims_ingestion",
        "severity": "medium",
        "category": "Volume Anomaly",
        "title": "Source row volume dropped by 68 percent",
        "root_cause": "One regional source partition was omitted from the upstream export manifest.",
        "recommendation": "Request the missing partition, pause downstream aggregation, then backfill and reconcile source-to-target counts.",
        "confidence": 0.88,
    },
}

def seed(db: Session):
    if db.query(Pipeline).count() == 0:
        now = datetime.utcnow()
        db.add_all([
            Pipeline(name="payments_stream", owner="Fintech Data", status="healthy", freshness_minutes=2, success_rate=99.7, last_run=now),
            Pipeline(name="customer_360_daily", owner="Growth Analytics", status="healthy", freshness_minutes=14, success_rate=98.9, last_run=now - timedelta(minutes=14)),
            Pipeline(name="claims_ingestion", owner="Healthcare Data", status="healthy", freshness_minutes=6, success_rate=99.3, last_run=now - timedelta(minutes=6)),
            Pipeline(name="feature_store_sync", owner="ML Platform", status="healthy", freshness_minutes=3, success_rate=99.8, last_run=now - timedelta(minutes=3)),
        ])
        db.commit()

def simulate(db: Session, scenario: str) -> Incident:
    data = SCENARIOS.get(scenario, SCENARIOS["schema_drift"])
    pipeline = db.query(Pipeline).filter(Pipeline.name == data["pipeline"]).first()
    if pipeline:
        pipeline.status = "degraded"
    incident = Incident(
        pipeline_name=data["pipeline"], severity=data["severity"], category=data["category"], title=data["title"],
        root_cause=data["root_cause"], recommendation=data["recommendation"], confidence=data["confidence"]
    )
    db.add(incident); db.commit(); db.refresh(incident)
    db.add(AuditEvent(incident_id=incident.id, action="AI_ROOT_CAUSE_ANALYSIS", actor="AegisFlow Agent", detail=f"Generated diagnosis with {incident.confidence:.0%} confidence."))
    db.commit()
    return incident

def resolve(db: Session, incident: Incident, actor: str):
    incident.status = "resolved"; incident.resolved_at = datetime.utcnow()
    pipeline = db.query(Pipeline).filter(Pipeline.name == incident.pipeline_name).first()
    if pipeline:
        pipeline.status = "healthy"; pipeline.last_run = datetime.utcnow(); pipeline.success_rate = min(99.9, pipeline.success_rate + 0.1)
    db.add(AuditEvent(incident_id=incident.id, action="REMEDIATION_APPROVED", actor=actor, detail="Safe remediation workflow executed and pipeline health restored."))
    db.commit(); db.refresh(incident)
    return incident
