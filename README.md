# AegisFlow AI

A production-oriented autonomous data-pipeline reliability platform built for AI Data Engineering and Data Platform portfolios.

## What it demonstrates

- Live pipeline health and reliability KPIs
- AI-assisted root-cause analysis for schema drift, freshness failures, and volume anomalies
- Human-in-the-loop, policy-governed remediation
- Full incident and action audit trail
- FastAPI/OpenAPI backend with PostgreSQL or zero-config SQLite
- Responsive Next.js + TypeScript command center
- Docker Compose, automated tests, and GitHub Actions CI
- Deployment-ready separation for Vercel and Render

## Architecture

```text
Next.js dashboard (Vercel)
          |
          | HTTPS / REST
          v
FastAPI reliability service (Render)
          |
          v
PostgreSQL (Render/Neon) or SQLite demo mode
```

The included simulator represents telemetry normally emitted by Kafka, Airflow/Dagster, dbt, Spark/Flink, Great Expectations, and OpenLineage. It keeps the hosted portfolio demo affordable while preserving a clean extension path to those systems.

## Local run — easiest method

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

### 2. Frontend

Open a second PowerShell window:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Application: `http://localhost:3000`

## Local run with Docker

```bash
docker compose up --build
```

## Deploy the API to Render

1. Push the repository to GitHub.
2. In Render, create a **New Web Service** from the repository.
3. Set **Root Directory** to `backend`.
4. Build command:

```text
pip install -r requirements.txt
```

5. Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Add environment variables:

```text
DATABASE_URL=sqlite:///./aegisflow.db
CORS_ORIGINS=https://YOUR-VERCEL-PROJECT.vercel.app
```

SQLite is sufficient for the portfolio demo. For persistent production storage, replace `DATABASE_URL` with a PostgreSQL connection string such as:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

7. Deploy and copy the Render API URL.

## Deploy the frontend to Vercel

1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Add:

```text
NEXT_PUBLIC_API_URL=https://YOUR-RENDER-API.onrender.com
```

4. Deploy.
5. Return to Render and set `CORS_ORIGINS` to the exact Vercel URL, then redeploy the API.

## GitHub commands

```powershell
git init
git add .
git commit -m "Build AegisFlow AI data reliability platform"
git branch -M main
git remote add origin https://github.com/Rajasrivatsansrinivasan/aegisflow-ai.git
git push -u origin main
```

## Resume-ready project entry

**AegisFlow AI — Autonomous Data Pipeline Reliability Platform**  
Built a full-stack DataOps platform using Next.js, TypeScript, FastAPI, PostgreSQL, SQLAlchemy, Docker, and GitHub Actions to monitor pipeline SLAs, detect schema and volume anomalies, generate root-cause diagnoses, and execute human-approved remediation workflows. Implemented incident lifecycle management, pipeline health metrics, confidence-scored recommendations, REST APIs, OpenAPI documentation, and an immutable audit trail, with independent Vercel and Render deployment support.

## Suggested next extensions

- Kafka event ingestion
- Airflow or Dagster integration
- Great Expectations validation results
- OpenLineage/Marquez lineage graph
- Prometheus/Grafana telemetry
- Ollama or Claude incident reasoning adapter
- Kubernetes Helm chart and Terraform
