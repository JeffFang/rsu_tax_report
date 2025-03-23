import csv
from datetime import datetime

def parse_sales_csv(csv_path):
    sales = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract date (MM/DD/YYYY → MM-DD-YYYY)
            date_str = row['Date & Time'].split()[0]
            date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%m-%d-%Y")
            
            sales.append({
                "type": "Sale",
                "date": date,
                "shares_sold": float(row["Sale Quantity"]),
                "sale_price_usd": float(row["Price"])
            })
    return sales