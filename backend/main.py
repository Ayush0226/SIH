import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from engine import OCRExtractor, MetrologyRuleEngine
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from supabase import create_client, Client

from dotenv import load_dotenv
load_dotenv()

# Environment variables (To be set in Render / .env)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_ANON_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

app = FastAPI(title="ComplyScan PWA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not supabase or SUPABASE_URL == "YOUR_SUPABASE_URL":
        # Mock user if Supabase isn't configured yet so frontend can be tested
        return {"id": "mock_user_id", "email": "officer@example.com"}
        
    token = credentials.credentials
    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.user
    except Exception as e:
        print("Auth error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/analyze")
async def analyze_product(
    category: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    os.makedirs("uploads", exist_ok=True)
    
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{timestamp_str}_{file.filename}"
    file_path = f"uploads/{safe_filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    # Extract Information (OCR + Regex)
    extractor = OCRExtractor()
    extracted_data = extractor.extract_information(file_path)
    
    # Run Legal Metrology Rule Engine
    engine = MetrologyRuleEngine(selected_category=category)
    report = engine.validate(extracted_data)
    
    # Generate Official PDF Report
    pdf_filename = f"report_{safe_filename}.pdf"
    pdf_path = f"uploads/{pdf_filename}"
    officer_email = getattr(current_user, 'email', 'officer@example.com') if hasattr(current_user, 'email') else current_user.get('email', 'mock@test.com')
    generate_pdf(pdf_path, officer_email, category, extracted_data, report)

    pdf_url = f"/api/download_report/{pdf_filename}"
    
    scan_id = None
    if supabase and SUPABASE_URL != "YOUR_SUPABASE_URL":
        try:
            user_id = getattr(current_user, 'id', 'mock_id') if hasattr(current_user, 'id') else current_user.get('id', 'mock_id')
            
            # Save to Supabase PostgreSQL Database
            result = supabase.table("scans").insert({
                "officer_id": user_id,
                "category": category,
                "image_filename": safe_filename,
                "pdf_url": pdf_url,
                "status": report["status"],
                "extracted_data": extracted_data,
                "violations": report["violations"]
            }).execute()
            scan_id = result.data[0]['id'] if result.data else None
        except Exception as e:
            print("DB Insert Error:", e)

    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://complyscan-backend.onrender.com").rstrip("/")

    return {
        "id": scan_id,
        "extracted_data": extracted_data,
        "report": report,
        "pdf_url": f"{base_url}{pdf_url}"
    }

@app.get("/api/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    if not supabase or SUPABASE_URL == "YOUR_SUPABASE_URL":
        return {"history": []}
        
    try:
        user_id = getattr(current_user, 'id', 'mock_id') if hasattr(current_user, 'id') else current_user.get('id', 'mock_id')
        response = supabase.table("scans").select("*").eq("officer_id", user_id).order("created_at", desc=True).execute()
        
        history = response.data
        base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://complyscan-backend.onrender.com").rstrip("/")
        for h in history:
            if h.get("pdf_url") and not h["pdf_url"].startswith("http"):
                h["pdf_url"] = f"{base_url}{h['pdf_url']}"
            elif h.get("pdf_url") and "127.0.0.1:8000" in h["pdf_url"]:
                h["pdf_url"] = h["pdf_url"].replace("http://127.0.0.1:8000", base_url)
                
        return {"history": history}
    except Exception as e:
        print("DB Select Error:", e)
        return {"history": []}

def generate_pdf(filename, officer_email, category, data, report):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "LEGAL METROLOGY COMPLIANCE REPORT")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, 700, f"Officer Email: {officer_email}")
    c.drawString(50, 680, f"Product Category: {category}")
    
    c.drawString(50, 640, "1. EXTRACTED LABEL DECLARATIONS:")
    y = 620
    for key, value in data.items():
        if value:
            readable_key = key.replace("_", " ").title()
            c.drawString(70, y, f"- {readable_key}: {value}")
            y -= 20
            
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    if report["status"] == "PASS":
        c.setFillColorRGB(0, 0.6, 0)
    else:
        c.setFillColorRGB(0.8, 0, 0)
    c.drawString(50, y, f"2. COMPLIANCE VERDICT: {report['status']}")
    
    y -= 30
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0, 0, 0)
    
    if report["violations"]:
        c.drawString(50, y, "Actionable Violations Noted under Rules, 2011:")
        y -= 20
        for i, v in enumerate(report["violations"], 1):
            c.drawString(70, y, f"{i}. {v}")
            y -= 20
    else:
        c.drawString(50, y, "All checked declarations appear compliant.")
        
    c.save()

@app.get("/api/download_report/{filename}")
async def download_report(filename: str):
    file_path = f"uploads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="Report not found")
