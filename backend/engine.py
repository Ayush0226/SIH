import re
import requests

class OCRExtractor:
    def __init__(self):
        # Using a free cloud OCR to bypass Render's 512MB RAM memory limits
        self.api_key = 'helloworld' # Free OCR.space API key
        print("Initialized Cloud OCR Engine!")

    def extract_information(self, filename: str):
        # 1. Send image to OCR.space API
        print(f"Sending {filename} to Cloud OCR...")
        with open(filename, 'rb') as f:
            r = requests.post(
                'https://api.ocr.space/parse/image',
                files={'filename': f},
                data={'apikey': self.api_key, 'language': 'eng'}
            )
        
        result = r.json()
        raw_text = ""
        results_list = []
        
        if result.get('ParsedResults'):
            raw_text = result['ParsedResults'][0].get('ParsedText', '').replace('\r', ' ').replace('\n', ' ')
            results_list = raw_text.split()
            
        print(f"--- RAW OCR TEXT EXTRACTED ---\n{raw_text}\n------------------------------")
        
        # 2. NLP/Regex: Structure the fields
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

        # Attempt to grab Product Name (Usually the first prominent text)
        if len(results_list) > 0:
            extracted["product_name"] = results_list[0]

        # Extract MRP
        mrp_match = re.search(r'(?i)(mrp|rs|₹|price)[\.\s:]*([\d\.]+)', raw_text)
        if mrp_match:
            extracted["mrp_raw"] = mrp_match.group(0)
            
            # Check if tax declaration is nearby
            tax_match = re.search(r'(?i)(incl.*?tax)', raw_text)
            if tax_match:
                extracted["mrp_raw"] += " " + tax_match.group(0)

        # Extract Net Quantity
        qty_match = re.search(r'(?i)(\d+)\s*(g|gm|gms|kg|ml|l|ltr)', raw_text)
        if qty_match:
            extracted["net_quantity_raw"] = qty_match.group(0)
            extracted["unit"] = qty_match.group(2).lower()

        # Extract FSSAI
        fssai_match = re.search(r'(?i)fssai.*?(1[0-9]{13})', raw_text)
        if fssai_match:
            extracted["fssai_no"] = fssai_match.group(1)

        # Extract Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        if email_match:
            extracted["consumer_care_email"] = email_match.group(0)

        # Extract Date
        date_match = re.search(r'(?i)(mfg|pkd|date).*?(\d{2}[/.\-]\d{4}|\d{2}[/.\-]\d{2})', raw_text)
        if date_match:
            extracted["mfg_date"] = date_match.group(0)

        return extracted

class MetrologyRuleEngine:
    def __init__(self, selected_category):
        self.category = selected_category
        self.report = {"status": "PASS", "violations": []}

    def validate(self, data: dict):
        if not data.get("product_name"):
            self.add_violation("Rule 6(1)(b) Violation: Missing Generic/Common Name.")
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
        valid_units = ["g", "kg", "ml", "l", "m", "cm", "n"]
        
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
