import csv, io, json, os, re, logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import create_engine, String, Text, DateTime, Integer, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from prometheus_client import Counter, make_asgi_app

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("lead-agent")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread":False} if DB_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
class Base(DeclarativeBase): pass
class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(200))
    contact_name: Mapped[str] = mapped_column(String(200), default="")
    email: Mapped[str] = mapped_column(String(320), index=True)
    website: Mapped[str] = mapped_column(String(500), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    employee_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="manual")
    notes: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0)
    priority: Mapped[str] = mapped_column(String(20), default="low")
    score_reason: Mapped[str] = mapped_column(Text, default="")
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
Base.metadata.create_all(engine)
CREATED = Counter("leads_created_total", "Lead records created")
app = FastAPI(title="AI Lead Generation Agent", version="1.0.0", description="Review-first lead qualification and scoring. No automated outreach.")
app.mount("/metrics", make_asgi_app())
app.mount("/ui", StaticFiles(directory=str(Path(__file__).parent.parent / "frontend"), html=True), name="ui")

class LeadIn(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact_name: str = Field(default="", max_length=200)
    email: EmailStr
    website: str = Field(default="", max_length=500)
    industry: str = Field(default="", max_length=120)
    employee_count: Optional[int] = Field(default=None, ge=0, le=10_000_000)
    source: str = Field(default="manual", max_length=80)
    notes: str = Field(default="", max_length=4000)

class ReviewIn(BaseModel):
    status: str = Field(pattern="^(qualified|disqualified|contacted)$")
    reviewer_note: str = Field(default="", max_length=2000)

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

def score_lead(x: LeadIn) -> tuple[float,str,str]:
    score=0; reasons=[]
    if x.website and re.match(r"^https?://", x.website.strip(), re.I): score+=20; reasons.append("website supplied (+20)")
    if x.industry.strip(): score+=20; reasons.append("industry supplied (+20)")
    if x.employee_count is not None:
        if x.employee_count >= 50: score+=25; reasons.append("50+ employees (+25)")
        elif x.employee_count >= 10: score+=15; reasons.append("10–49 employees (+15)")
        else: score+=5; reasons.append("1–9 employees (+5)")
    if x.contact_name.strip(): score+=10; reasons.append("named contact supplied (+10)")
    if len(x.notes.strip()) >= 30: score+=25; reasons.append("substantive business context supplied (+25)")
    priority = "high" if score>=70 else "medium" if score>=40 else "low"
    return score, priority, "; ".join(reasons) if reasons else "Limited verified information supplied; manual research required."

def ai_summarize(lead: Lead) -> str:
    key=os.getenv("OPENAI_API_KEY")
    if not key: return "AI summary unavailable: configure OPENAI_API_KEY. Use supplied fields only; no external research has been performed."
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        data={"company":lead.company,"industry":lead.industry,"employee_count":lead.employee_count,"website":lead.website,"notes":lead.notes}
        response=client.chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),temperature=0.1,messages=[{"role":"system","content":"Summarize only the supplied business information. Do not invent facts, infer sensitive personal traits, claim to browse, or assert buying intent without evidence. Clearly label unknowns."},{"role":"user","content":json.dumps(data)}])
        return response.choices[0].message.content or "No summary returned."
    except Exception as e:
        logger.warning(json.dumps({"event":"ai_summary_fallback","error":type(e).__name__}))
        return "AI summary failed; review the supplied source data manually."

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/leads",status_code=201)
def create_lead(payload:LeadIn,db:Session=Depends(get_db)):
    existing=db.scalar(select(Lead).where(Lead.email==str(payload.email)))
    if existing: raise HTTPException(409,"A lead with this email already exists")
    score,priority,reason=score_lead(payload)
    row=Lead(**payload.model_dump(),email=str(payload.email),score=score,priority=priority,score_reason=reason)
    db.add(row);db.commit();db.refresh(row);CREATED.inc()
    logger.info(json.dumps({"event":"lead_created","lead_id":row.id,"priority":priority}))
    return serialize(row)

@app.post("/leads/import-csv",status_code=201)
async def import_csv(file:UploadFile=File(...),db:Session=Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Upload a .csv file")
    raw=await file.read()
    if len(raw)>2_000_000: raise HTTPException(413,"CSV limit is 2 MB")
    try: rows=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    except UnicodeDecodeError: raise HTTPException(400,"CSV must be UTF-8 encoded")
    required={"company","email"}
    if not rows.fieldnames or not required.issubset({x.strip().lower() for x in rows.fieldnames}): raise HTTPException(400,"CSV requires company,email headers")
    created=[]; errors=[]
    for n,row in enumerate(rows,start=2):
        data={k.strip().lower(): (v or "").strip() for k,v in row.items() if k}
        try:
            payload=LeadIn(company=data.get("company",""),email=data.get("email",""),contact_name=data.get("contact_name",""),website=data.get("website",""),industry=data.get("industry",""),employee_count=int(data["employee_count"]) if data.get("employee_count") else None,source=data.get("source","csv"),notes=data.get("notes",""))
            if db.scalar(select(Lead).where(Lead.email==str(payload.email))): errors.append({"row":n,"error":"duplicate email"});continue
            s,p,r=score_lead(payload); item=Lead(**payload.model_dump(),email=str(payload.email),score=s,priority=p,score_reason=r);db.add(item);db.flush();created.append(item.id);CREATED.inc()
        except Exception as exc: errors.append({"row":n,"error":str(exc)[:200]})
    db.commit()
    return {"created_count":len(created),"created_ids":created,"errors":errors}

def serialize(x): return {"id":x.id,"company":x.company,"contact_name":x.contact_name,"email":x.email,"website":x.website,"industry":x.industry,"employee_count":x.employee_count,"source":x.source,"score":x.score,"priority":x.priority,"score_reason":x.score_reason,"ai_summary":x.ai_summary,"status":x.status,"created_at":x.created_at}

@app.get("/leads")
def list_leads(priority:Optional[str]=None,db:Session=Depends(get_db)):
    q=select(Lead).order_by(Lead.score.desc(),Lead.id.desc())
    if priority:
        if priority not in ["high","medium","low"]: raise HTTPException(400,"priority must be high, medium, or low")
        q=q.where(Lead.priority==priority)
    return [serialize(x) for x in db.scalars(q.limit(500)).all()]

@app.get("/leads/{lead_id}")
def get_lead(lead_id:int,db:Session=Depends(get_db)):
    x=db.get(Lead,lead_id)
    if not x: raise HTTPException(404,"Lead not found")
    return serialize(x)

@app.post("/leads/{lead_id}/summarize")
def summarize(lead_id:int,db:Session=Depends(get_db)):
    x=db.get(Lead,lead_id)
    if not x: raise HTTPException(404,"Lead not found")
    x.ai_summary=ai_summarize(x);db.commit();return {"lead_id":x.id,"summary":x.ai_summary}

@app.post("/leads/{lead_id}/review")
def review(lead_id:int,payload:ReviewIn,db:Session=Depends(get_db)):
    x=db.get(Lead,lead_id)
    if not x: raise HTTPException(404,"Lead not found")
    x.status=payload.status
    x.notes=(x.notes+"\nReviewer: "+payload.reviewer_note).strip()[:4000] if payload.reviewer_note else x.notes
    db.commit();return {"lead_id":x.id,"status":x.status,"message":"Review recorded. No email or outreach was sent."}

@app.get("/reports/summary")
def report(db:Session=Depends(get_db)):
    items=db.scalars(select(Lead)).all()
    return {"total_leads":len(items),"high_priority":sum(x.priority=="high" for x in items),"medium_priority":sum(x.priority=="medium" for x in items),"low_priority":sum(x.priority=="low" for x in items),"qualified":sum(x.status=="qualified" for x in items),"reviewed":sum(x.status in ("qualified","disqualified","contacted") for x in items),"qualification_rate_of_reviewed":round(sum(x.status=="qualified" for x in items)/max(1,sum(x.status in ("qualified","disqualified","contacted") for x in items)),3)}
