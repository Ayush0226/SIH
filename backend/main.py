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
    width, height = letter

    # 1. Header Banner
    c.setFillColorRGB(0.1, 0.22, 0.5)
    c.rect(0, height - 90, width, 90, fill=1, stroke=0)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 35, "GOVERNMENT OF INDIA - MINISTRY OF CONSUMER AFFAIRS")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 52, "DIRECTORATE OF LEGAL METROLOGY | PACKAGED COMMODITIES INSPECTION")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, height - 70, "Inspection Report generated under Legal Metrology (Packaged Commodities) Rules, 2011")

    # 2. Metadata Box
    c.setFillColorRGB(0.96, 0.97, 0.99)
    c.setStrokeColorRGB(0.85, 0.88, 0.92)
    c.roundRect(40, height - 165, width - 80, 60, 6, fill=1, stroke=1)
    
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, height - 120, f"Inspection Date: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    c.drawString(55, height - 145, f"Officer Email: {officer_email}")
    c.drawString(340, height - 120, f"Product Category: {category}")
    c.drawString(340, height - 145, "Inspection Mode: Mobile OCR & Metrology Engine")

    # 3. Compliance Verdict Box
    is_pass = (report.get("status") == "PASS")
    if is_pass:
        c.setFillColorRGB(0.92, 0.98, 0.93)
        c.setStrokeColorRGB(0.2, 0.65, 0.3)
        status_text = "VERDICT: COMPLIANT (PASS)"
        text_color = (0.05, 0.45, 0.15)
    else:
        c.setFillColorRGB(0.99, 0.93, 0.93)
        c.setStrokeColorRGB(0.85, 0.2, 0.2)
        status_text = "VERDICT: STATUTORY VIOLATION DETECTED"
        text_color = (0.75, 0.1, 0.1)

    c.roundRect(40, height - 215, width - 80, 40, 6, fill=1, stroke=1)
    c.setFillColorRGB(*text_color)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(55, height - 200, status_text)

    # 4. Mandatory Extracted Declarations
    c.setFillColorRGB(0.1, 0.2, 0.3)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 240, "1. MANDATORY PACKAGING DECLARATIONS (RULE 6)")

    # Draw declarations table
    y = height - 265
    fields_order = [
        ("product_name", "Common / Generic Commodity Name"),
        ("mrp_raw", "Maximum Retail Price (MRP)"),
        ("net_quantity_raw", "Net Quantity (with SI Unit)"),
        ("usp_raw", "Unit Sale Price (USP)"),
        ("mfg_date", "Date of Manufacture / Packing"),
        ("batch_no", "Batch / Lot Identification"),
        ("manufacturer_details", "Name & Address of Manufacturer / Packer"),
        ("fssai_no", "FSSAI License No. (Food Commodities)"),
        ("country_of_origin", "Country of Origin"),
        ("consumer_care_phone", "Consumer Care Contact Number"),
        ("consumer_care_email", "Consumer Care Email Address")
    ]

    for key, label in fields_order:
        val = data.get(key)
        if val:
            c.setFont("Helvetica-Bold", 9)
            c.setFillColorRGB(0.25, 0.3, 0.35)
            c.drawString(45, y, f"{label}:")
            
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            # Truncate long addresses for single line
            val_str = str(val)
            if len(val_str) > 75:
                val_str = val_str[:72] + "..."
            c.drawString(245, y, val_str)
            y -= 17

    # 5. Violations & Observations
    y -= 15
    c.setFillColorRGB(0.1, 0.2, 0.3)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "2. STATUTORY OBSERVATIONS & ACTIONABLE CLAUSES")
    y -= 20

    if report.get("violations"):
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.8, 0.1, 0.1)
        for i, viol in enumerate(report["violations"], 1):
            c.drawString(45, y, f"[{i}] {viol}")
            y -= 16
    else:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.5, 0.2)
        c.drawString(45, y, "All verified declarations comply with Legal Metrology (Packaged Commodities) Rules, 2011.")
        y -= 18

    # 6. Official Footer & Seal Notice
    c.setStrokeColorRGB(0.85, 0.88, 0.92)
    c.line(40, 60, width - 40, 60)
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40, 45, "This document is an automated electronic inspection certificate pursuant to the Legal Metrology Act, 2009.")
    c.drawString(40, 32, "Verified with SIH 26034 ComplyScan AI Metrology System.")

    c.save()

@app.get("/api/download_report/{filename}")
async def download_report(filename: str):
    file_path = f"uploads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="Report not found")
