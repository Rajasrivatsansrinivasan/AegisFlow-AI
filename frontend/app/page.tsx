'use client';
import { useCallback, useEffect, useState } from 'react';
import { Activity, ShieldCheck, Sparkles, RefreshCw, CheckCircle2 } from 'lucide-react';

const API=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
type Overview={pipelines:number;healthy:number;open_incidents:number;critical_incidents:number;avg_success_rate:number;mttr_minutes:number};
type Pipeline={id:number;name:string;owner:string;status:string;freshness_minutes:number;success_rate:number;last_run:string};
type Incident={id:number;pipeline_name:string;severity:string;category:string;title:string;root_cause:string;recommendation:string;confidence:number;status:string;created_at:string};
type Audit={id:number;incident_id:number;action:string;actor:string;detail:string;created_at:string};
const initial:Overview={pipelines:0,healthy:0,open_incidents:0,critical_incidents:0,avg_success_rate:0,mttr_minutes:0};

export default function Home(){
 const [overview,setOverview]=useState(initial),[pipelines,setPipelines]=useState<Pipeline[]>([]),[incidents,setIncidents]=useState<Incident[]>([]),[audit,setAudit]=useState<Audit[]>([]),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const load=useCallback(async()=>{try{setError('');const [o,p,i,a]=await Promise.all(['overview','pipelines','incidents','audit'].map(x=>fetch(`${API}/api/${x}`,{cache:'no-store'})));if(!o.ok)throw new Error('API unavailable');setOverview(await o.json());setPipelines(await p.json());setIncidents(await i.json());setAudit(await a.json())}catch(e){setError('Backend is not connected. Set NEXT_PUBLIC_API_URL to your deployed API URL.')}},[]);
 useEffect(()=>{load()},[load]);
 async function simulate(scenario:string){setBusy(true);await fetch(`${API}/api/incidents/simulate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scenario})});await load();setBusy(false)}
 async function resolve(id:number){setBusy(true);await fetch(`${API}/api/incidents/${id}/resolve`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actor:'Data Platform Engineer'})});await load();setBusy(false)}
 const open=incidents.filter(x=>x.status==='open');
 return <main className="shell">
  <header className="top"><div className="brand"><div className="logo"><ShieldCheck size={24}/></div><div><h1>AegisFlow AI</h1><p>Autonomous Data Reliability Platform</p></div></div><div className="live"><span className="dot"/>Monitoring active</div></header>
  <section className="hero"><div><div className="eyebrow">DataOps command center</div><h2>Detect. Diagnose. Recover.</h2><p>Monitor critical pipelines, investigate failures with AI-assisted root-cause analysis, and execute policy-governed remediation with a complete audit trail.</p></div><div className="actions"><button className="btn" disabled={busy} onClick={()=>simulate('freshness')}>Test SLA breach</button><button className="btn primary" disabled={busy} onClick={()=>simulate('schema_drift')}><Sparkles size={15} style={{verticalAlign:'middle',marginRight:7}}/>Simulate incident</button></div></section>
  {error&&<div className="card" style={{borderColor:'var(--red)',color:'var(--red)'}}>{error}</div>}
  <section className="metrics">
   {[['Monitored pipelines',overview.pipelines,'4 production domains'],['Healthy now',overview.healthy,`${overview.pipelines?Math.round(overview.healthy/overview.pipelines*100):0}% availability`],['Open incidents',overview.open_incidents,`${overview.critical_incidents} critical`],['Success rate',`${overview.avg_success_rate}%`,'Across last 30 days'],['Mean recovery',`${overview.mttr_minutes} min`,'Policy-assisted MTTR']].map((m,i)=><div className="metric" key={i}><div className="label">{m[0]}</div><div className="value">{m[1]}</div><div className="sub">{m[2]}</div></div>)}
  </section>
  <section className="grid"><div>
   <div className="card"><div className="card-head"><div><div className="eyebrow">Live health</div><h3>Pipeline estate</h3></div><Activity size={20}/></div>{pipelines.map(p=><div className="pipeline" key={p.id}><div><div className="name">{p.name}</div><div className="small">Freshness: {p.freshness_minutes} min</div></div><div className="owner small">{p.owner}</div><div>{p.success_rate.toFixed(1)}%</div><div><span className={`badge ${p.status}`}>{p.status}</span></div></div>)}</div>
   <div className="card"><div className="card-head"><div><div className="eyebrow">Governed automation</div><h3>Incident intelligence</h3></div><RefreshCw size={18}/></div>{open.length===0?<div className="empty"><CheckCircle2 size={31}/><p>No active incidents. Your monitored pipelines are healthy.</p></div>:open.map(x=><div className={`incident ${x.severity}`} key={x.id}><div className="meta"><span className="badge degraded">{x.severity}</span><span>{x.category}</span><span>•</span><span>{x.pipeline_name}</span></div><h4>{x.title}</h4><p><strong>AI root cause:</strong> {x.root_cause}</p><p><strong>Safe remediation:</strong> {x.recommendation}</p><div className="confidence"><span className="small">Diagnostic confidence: {(x.confidence*100).toFixed(0)}%</span><button className="btn primary" disabled={busy} onClick={()=>resolve(x.id)}>Approve remediation</button></div></div>)}</div>
  </div><aside><div className="card"><div className="card-head"><div><div className="eyebrow">Immutable history</div><h3>Audit events</h3></div></div>{audit.length===0?<div className="empty">Actions will appear after an incident is detected.</div>:audit.map(a=><div className="audit" key={a.id}><strong>{a.action.replaceAll('_',' ')}</strong><div className="small">{a.actor} · Incident #{a.incident_id}</div><div className="small">{a.detail}</div></div>)}</div><div className="card"><div className="eyebrow">Architecture</div><h3>Production-oriented stack</h3><p className="small" style={{lineHeight:1.7}}>Next.js · TypeScript · FastAPI · SQLAlchemy · PostgreSQL · Docker · GitHub Actions · OpenAPI · policy-governed remediation</p></div></aside></section>
  <footer className="footer">AegisFlow AI · Built for AI Data Engineering and Data Platform portfolios</footer>
 </main>
}
