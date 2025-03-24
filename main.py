import os
from datetime import datetime
from decimal import Decimal, getcontext
from pdf_parser import extract_pdf_data
from exchange_rate import get_exchange_rate
from tax_calculator import calculate_tax_data, process_sale
from spreadsheet_updater import update_spreadsheet, create_annual_summary
from sales_parser import parse_sales_csv

getcontext().prec = 8  # Precision for financial calculations

def process_all_data(pdf_dir="pdfs", sales_csv="sells.csv"):
    # Initialize tracking in both USD and CAD
    current_shares = Decimal('0')
    current_acb_usd = Decimal('0')
    current_acb_cad = Decimal('0')
    
    # Load all transactions
    all_data = []
    
    # 1. Process PDFs (RSU/ESPP)
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            try:
                pdf_path = os.path.join(pdf_dir, filename)
                data = extract_pdf_data(pdf_path)
                all_data.append(data)
            except Exception as e:
                print(f"Skipped {filename}: {str(e)}")
    
    # 2. Process Sales CSV
    try:
        sales = parse_sales_csv(sales_csv)
        all_data.extend(sales)
    except FileNotFoundError:
        print(f"Error: {sales_csv} not found!")
    
    # 3. Sort by date
    all_data.sort(key=lambda x: datetime.strptime(x["date"], "%m-%d-%Y"))
    
    # 4. Process transactions with USD-first tracking
    for transaction in all_data:
        try:
            exchange_rate = get_exchange_rate(transaction["date"])
            exchange_rate_dec = Decimal(str(exchange_rate))
            
            if transaction["type"] == "RSU":
                # Verify required fields exist
                if "shares_vested" not in transaction:
                    raise KeyError(f"Missing 'shares_vested' in RSU transaction: {transaction}")
                
                # ------------------------------------------
                # Part 1: Vesting (USD-based ACB)
                # ------------------------------------------
                vest_data = {
                    "type": "RSU_Vest",
                    "date": transaction["date"],
                    "shares": transaction["shares_vested"],
                    "fmv_usd": transaction["fmv_usd"]
                }
                tax_data = calculate_tax_data(vest_data, exchange_rate)
                
                # Update tracking in USD first
                shares_added = Decimal(str(vest_data["shares"]))
                current_shares += shares_added
                current_acb_usd += Decimal(str(tax_data["total_acb_usd"]))
                current_acb_cad = current_acb_usd * exchange_rate_dec
                
                update_spreadsheet(
                    vest_data, tax_data, exchange_rate,
                    float(current_shares),
                    float(current_acb_usd),
                    float(current_acb_cad),
                    output_path="stock_tracker.xlsx"
                )
                
                # ------------------------------------------
                # Part 2: Sale-to-Cover (USD-based calculation)
                # ------------------------------------------
                if "shares_sold" in transaction and transaction["shares_sold"] > 0:
                    sale_data = {
                        "type": "Sale_to_Cover",
                        "date": transaction["date"],
                        "shares_sold": transaction["shares_sold"],
                        "sale_price_usd": transaction["sale_price_usd"]
                    }
                    
                    # Process sale using USD ACB
                    sale_tax_data = process_sale(
                        sale_data, 
                        float(current_shares), 
                        float(current_acb_usd), 
                        exchange_rate
                    )
                    
                    # Update tracking
                    shares_sold = Decimal(str(sale_data["shares_sold"]))
                    current_shares -= shares_sold
                    current_acb_usd -= Decimal(str(sale_tax_data["acb_sold_usd"]))
                    current_acb_cad = current_acb_usd * exchange_rate_dec
                    
                    update_spreadsheet(
                        sale_data, sale_tax_data, exchange_rate,
                        float(current_shares),
                        float(current_acb_usd),
                        float(current_acb_cad),
                        output_path="stock_tracker.xlsx"
                    )

            elif transaction["type"] == "ESPP":
                tax_data = calculate_tax_data(transaction, exchange_rate)
                
                # Update USD tracking
                shares_added = Decimal(str(transaction["shares"]))
                current_shares += shares_added
                current_acb_usd += Decimal(str(tax_data["total_acb_usd"]))
                current_acb_cad = current_acb_usd * exchange_rate_dec
                
                update_spreadsheet(
                    transaction, 
                    tax_data, 
                    exchange_rate,
                    float(current_shares),
                    float(current_acb_usd),
                    float(current_acb_cad),
                    output_path="stock_tracker.xlsx"
                )
                
            elif transaction["type"] == "Sale":
                if current_shares <= 0:
                    print(f"Error: No shares to sell on {transaction['date']}!")
                    continue
                
                # Process sale using USD ACB
                sale_tax_data = process_sale(
                    transaction, 
                    float(current_shares), 
                    float(current_acb_usd), 
                    exchange_rate
                )
                
                # Update tracking
                shares_sold = Decimal(str(transaction["shares_sold"]))
                current_shares -= shares_sold
                current_acb_usd -= Decimal(str(sale_tax_data["acb_sold_usd"]))
                current_acb_cad = current_acb_usd * exchange_rate_dec
                
                update_spreadsheet(
                    transaction, 
                    sale_tax_data, 
                    exchange_rate,
                    float(current_shares),
                    float(current_acb_usd),
                    float(current_acb_cad),
                    output_path="stock_tracker.xlsx"
                )
                
        except Exception as e:
            print(f"Failed {transaction.get('date', 'N/A')}: {str(e)}")

    create_annual_summary("stock_tracker.xlsx")

if __name__ == "__main__":
    process_all_data()