from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .config import settings
from .database import Base, engine, get_db
from .models import Pipeline, Incident, AuditEvent
from .schemas import PipelineOut, IncidentOut, AuditOut, SimulateRequest, ResolveRequest
from .service import seed, simulate, resolve

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Autonomous data-pipeline reliability and remediation platform")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    from .database import SessionLocal
    db = SessionLocal(); seed(db); db.close()

@app.get("/")
def root(): return {"service": settings.app_name, "status": "operational", "docs": "/docs"}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/overview")
def overview(db: Session = Depends(get_db)):
    pipelines = db.query(Pipeline).all(); incidents = db.query(Incident).all()
    open_incidents = [i for i in incidents if i.status == "open"]
    return {
        "pipelines": len(pipelines), "healthy": sum(p.status == "healthy" for p in pipelines),
        "open_incidents": len(open_incidents), "critical_incidents": sum(i.severity == "critical" and i.status == "open" for i in incidents),
        "avg_success_rate": round(sum(p.success_rate for p in pipelines) / max(len(pipelines), 1), 2),
        "mttr_minutes": 8.4,
    }

@app.get("/api/pipelines", response_model=list[PipelineOut])
def pipelines(db: Session = Depends(get_db)): return db.query(Pipeline).order_by(Pipeline.id).all()

@app.get("/api/incidents", response_model=list[IncidentOut])
def incidents(db: Session = Depends(get_db)): return db.query(Incident).order_by(desc(Incident.created_at)).limit(50).all()

@app.post("/api/incidents/simulate", response_model=IncidentOut)
def simulate_incident(payload: SimulateRequest, db: Session = Depends(get_db)): return simulate(db, payload.scenario)

@app.post("/api/incidents/{incident_id}/resolve", response_model=IncidentOut)
def resolve_incident(incident_id: int, payload: ResolveRequest, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident: raise HTTPException(404, "Incident not found")
    if incident.status == "resolved": return incident
    return resolve(db, incident, payload.actor)

@app.get("/api/audit", response_model=list[AuditOut])
def audit(db: Session = Depends(get_db)): return db.query(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(50).all()
