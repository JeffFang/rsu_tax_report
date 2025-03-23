import pdfplumber
import re

def extract_pdf_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        
        if "EMPLOYEE STOCK PLAN RELEASE CONFIRMATION" in text:
            return extract_rsu_data(text)
        elif "EMPLOYEE STOCK PLAN PURCHASE CONFIRMATION" in text:
            return extract_espp_data(text)
        else:
            raise ValueError("Unsupported PDF type")

def extract_rsu_data(text):
    data = {"type": "RSU"}
    
    # Extract Release Date
    date_match = re.search(r"Release Date\s+(\d{2}-\d{2}-\d{4})", text)
    data["date"] = date_match.group(1) if date_match else None
    
    # Extract Shares Released (Vested)
    shares_vested_match = re.search(r"Shares Released\s+([\d.]+)", text)
    data["shares_vested"] = float(shares_vested_match.group(1)) if shares_vested_match else 0.0
    
    # Extract FMV per Share
    fmv_match = re.search(r"Market Value Per Share\s+\$([\d.]+)", text)
    data["fmv_usd"] = float(fmv_match.group(1)) if fmv_match else 0.0
    
    # Extract Shares Sold (for taxes)
    shares_sold_match = re.search(r"Shares Sold\s+\(([\d.]+)\)", text)
    data["shares_sold"] = float(shares_sold_match.group(1)) if shares_sold_match else 0.0
    
    # Extract Sale Price per Share (for sell-to-cover)
    sale_price_match = re.search(r"Sale Price Per Share\s+\$([\d.]+)", text)
    data["sale_price_usd"] = float(sale_price_match.group(1)) if sale_price_match else 0.0
    
    return data

def extract_espp_data(text):
    data = {"type": "ESPP"}
    data["date"] = re.search(r"Purchase Date\s+(\d{2}-\d{2}-\d{4})", text).group(1)
    data["shares"] = float(re.search(r"Shares Purchased\s+([\d.]+)", text).group(1))
    data["fmv_usd"] = float(re.search(r"Purchase Value per Share\s+\$([\d.]+)", text).group(1))
    data["purchase_price_usd"] = float(re.search(r"\((\d+\.\d+)% of \$[\d.]+\)\s+\$([\d.]+)", text).group(2))
    return data