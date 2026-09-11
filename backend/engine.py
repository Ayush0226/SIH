import re
import io
import requests
from PIL import Image

class OCRExtractor:
    def __init__(self):
        # Active OCR API keys with automatic fallback
        self.api_keys = ['K87899148888957', 'K88537684888957', 'K82348581688957']
        print("Initialized Cloud OCR Engine with Multi-Key Fallback!")

    def extract_information(self, filename: str):
        raw_text = ""
        
        # 1. Convert input image (supports WEBP, PNG, JPG, BMP) to JPEG buffer using Pillow
        try:
            with Image.open(filename) as img:
                rgb_img = img.convert('RGB')
                buf = io.BytesIO()
                rgb_img.save(buf, format='JPEG', quality=95)
                image_bytes = buf.getvalue()
        except Exception as e:
            print("Image conversion error:", e)
            with open(filename, 'rb') as f:
                image_bytes = f.read()

        # 2. Query Cloud OCR API with key fallback
        for key in self.api_keys:
            try:
                print(f"Attempting Cloud OCR with key prefix {key[:4]}...")
                r = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'file': ('image.jpg', image_bytes, 'image/jpeg')},
                    data={'apikey': key, 'language': 'eng', 'OCREngine': '2'},
                    timeout=20
                )
                res = r.json()
                if res.get('ParsedResults') and len(res['ParsedResults']) > 0:
                    raw_text = res['ParsedResults'][0].get('ParsedText', '')
                    if raw_text.strip():
                        print("OCR extraction successful!")
                        break
                elif res.get('ErrorMessage'):
                    print(f"OCR key {key[:4]} error:", res.get('ErrorMessage'))
            except Exception as ex:
                print(f"OCR request failed for key {key[:4]}:", ex)

        print(f"--- RAW OCR TEXT EXTRACTED ---\n{raw_text}\n------------------------------")
        
        # 3. NLP/Regex: Structure the fields
        extracted = {
            "product_name": None,
            "mrp_raw": None,
            "net_quantity_raw": None,
            "unit": None,
            "mrp_value": None,
            "net_quantity_value": None,
            "mfg_date": None,
            "manufacturer_details": None,
            "consumer_care_email": None,
            "consumer_care_phone": None,
            "fssai_no": None,
            "country_of_origin": None,
            "usp_raw": None
        }

        if not raw_text.strip():
            extracted["product_name"] = "Unreadable or Blank Image"
            return extracted

        # Split into clean lines
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        if lines:
            extracted["product_name"] = lines[0]

        # Extract MRP
        mrp_match = re.search(r'(?i)(?:mrp|rs|₹|price|as)[\.\s:]*([\d\.]+)', raw_text)
        if mrp_match:
            extracted["mrp_raw"] = mrp_match.group(0)
            tax_match = re.search(r'(?i)(incl.*?tax[a-z]*)', raw_text)
            if tax_match:
                extracted["mrp_raw"] += " " + tax_match.group(0)

        # Extract Net Quantity & Unit
        qty_match = re.search(r'(?i)(\d+(?:\.\d+)?)\s*(g|gm|gms|kg|ml|l|ltr|oz|mg)\b', raw_text)
        if qty_match:
            extracted["net_quantity_raw"] = qty_match.group(0)
            extracted["unit"] = qty_match.group(2).lower()

        # Extract Mfg/Packing Date
        date_match = re.search(r'(?i)(?:mfg|pkd|date|packed|use\s*by|exp)[\.\s:]*([0-9]{1,2}[/.\-][0-9]{2,4})', raw_text)
        if date_match:
            extracted["mfg_date"] = date_match.group(0)

        # Extract Manufacturer / Packer Details
        mfg_match = re.search(r'(?i)(?:mfg\s*by|manufactured\s*by|packed\s*by|marketed\s*by)[\.\s:]*([^\n\r]+)', raw_text)
        if mfg_match:
            extracted["manufacturer_details"] = mfg_match.group(0).strip()

        # Extract Country of Origin
        origin_match = re.search(r'(?i)(?:country\s*of\s*origin|made\s*in|product\s*of)[\.\s:]*([a-zA-Z\s]+)', raw_text)
        if origin_match:
            extracted["country_of_origin"] = origin_match.group(0).strip()

        # Extract FSSAI License Number (14 digits)
        fssai_match = re.search(r'(?i)(?:fssai|lic)[\.\s:a-z]*([0-9]{14})', raw_text)
        if fssai_match:
            extracted["fssai_no"] = fssai_match.group(1)

        # Extract Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        if email_match:
            extracted["consumer_care_email"] = email_match.group(0)

        # Extract Phone / Helpline
        phone_match = re.search(r'(?i)(?:tel|phone|helpline|care)[\.\s:]*([0-9\-]{8,12})', raw_text)
        if phone_match:
            extracted["consumer_care_phone"] = phone_match.group(1)

        return extracted

class MetrologyRuleEngine:
    def __init__(self, selected_category):
        self.category = selected_category
        self.report = {"status": "PASS", "violations": []}

    def validate(self, data: dict):
        if not data.get("product_name") or data.get("product_name") == "Unreadable or Blank Image":
            self.add_violation("Rule 6(1)(b) Violation: Missing or unreadable Generic/Common Name.")
        if not data.get("mrp_raw"):
            self.add_violation("Rule 6(1)(e) Violation: Missing Maximum Retail Price (MRP).")
        if not data.get("net_quantity_raw"):
            self.add_violation("Rule 6(1)(c) Violation: Missing Net Quantity.")
        if not data.get("mfg_date"):
            self.add_violation("Rule 6(1)(d) Violation: Missing Month and Year of Manufacture/Packing.")
        if not data.get("manufacturer_details"):
            self.add_violation("Rule 6(1)(a) Violation: Missing Manufacturer/Packer Name & Address.")
        if not data.get("consumer_care_email") and not data.get("consumer_care_phone"):
            self.add_violation("Rule 6(1)(n) Violation: Missing Consumer Care Contact Details.")
        if not data.get("country_of_origin"):
            self.add_violation("Rule 6(1)(a) Violation: Missing Country Of Origin declaration.")

        mrp_text = data.get("mrp_raw", "").lower() if data.get("mrp_raw") else ""
        if mrp_text and "tax" not in mrp_text:
            self.add_violation("Rule 6(1)(e) Format Violation: MRP must explicitly state 'inclusive of all taxes'.")

        extracted_unit = data.get("unit", "").lower() if data.get("unit") else ""
        illegal_units = ["gm", "gms", "ltr", "kilos", "kilo"]
        valid_units = ["g", "kg", "ml", "l", "m", "cm", "n", "mg"]
        
        if extracted_unit in illegal_units:
            self.add_violation(f"Schedule II Violation: Illegal unit '{extracted_unit}' used. Standard SI unit must be used (e.g., 'g', 'kg').")
        elif extracted_unit and extracted_unit not in valid_units:
             self.add_violation(f"Schedule II Warning: Unrecognized unit '{extracted_unit}'.")

        if self.category == "Food":
            if not data.get("fssai_no"):
                self.add_violation("Category Specific Violation: Food items must display FSSAI License Number.")
                
        return self.report

    def add_violation(self, reason):
        self.report["status"] = "VIOLATION DETECTED"
        self.report["violations"].append(reason)
