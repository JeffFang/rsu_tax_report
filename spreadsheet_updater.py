import pandas as pd

COLUMNS = [
    "Date", 
    "Type",
    "Shares Added/Sold",  # Negative for sales
    "FMV (USD)",
    "FMV (CAD)",
    "Purchase Price (USD)",
    "Purchase Price (CAD)",
    "Sale Price (USD)",
    "Sale Price (CAD)",
    "Exchange Rate",
    "Taxable Income (CAD)", 
    "ACB Impact (CAD)",
    "Capital Gain/Loss (CAD)",
    "Shares Remaining",
    "ACB Remaining (CAD)"
]

def update_spreadsheet(data, tax_data, exchange_rate, shares_remaining, acb_remaining, output_path="stock_tracker.xlsx"):
    try:
        df = pd.read_excel(output_path, sheet_name="Transactions")
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNS)
    
    new_row = {
        "Date": data["date"],
        "Type": data["type"],
        "Exchange Rate": exchange_rate,
        "Shares Remaining": shares_remaining,
        "ACB Remaining (CAD)": acb_remaining
    }

    if data["type"] in ["RSU", "ESPP"]:
        new_row.update({
            "Shares Added/Sold": data["shares"],
            "FMV (USD)": data["fmv_usd"],
            "FMV (CAD)": data["fmv_usd"] * exchange_rate,
            "Purchase Price (USD)": data.get("purchase_price_usd", None),
            "Purchase Price (CAD)": data.get("purchase_price_usd", 0) * exchange_rate,
            "Taxable Income (CAD)": tax_data["taxable_income_cad"],
            "ACB Impact (CAD)": tax_data["total_acb"],
            "Capital Gain/Loss (CAD)": tax_data["capital_gain_loss"]
        })
    elif data["type"] == "Sale":
        new_row.update({
            "Shares Added/Sold": -data["shares_sold"],  # Negative for sales
            "Sale Price (USD)": data["sale_price_usd"],
            "Sale Price (CAD)": data["sale_price_usd"] * exchange_rate,
            "ACB Impact (CAD)": -tax_data["acb_sold_cad"],  # Negative ACB impact
            "Capital Gain/Loss (CAD)": tax_data["capital_gain_loss"]
        })

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = df[COLUMNS]  # Maintain column order
    df.to_excel(output_path, sheet_name="Transactions", index=False)

def create_annual_summary(output_path="stock_tracker.xlsx"):
    """Generate an annual summary of proceeds, cost basis, and capital gains."""
    try:
        # Read transactions sheet
        df = pd.read_excel(output_path, sheet_name="Transactions")
    except FileNotFoundError:
        print("Error: Transactions sheet not found.")
        return
    except ValueError as e:
        print(f"Error reading sheet: {str(e)}")
        return

    # Filter only sales (Sale and Sale_to_Cover)
    sales_df = df[df["Type"].isin(["Sale", "Sale_to_Cover"])].copy()
    
    if sales_df.empty:
        print("No sales data to summarize.")
        return
    
    # Extract year from date
    sales_df["Year"] = pd.to_datetime(sales_df["Date"]).dt.year
    
    # Calculate proceeds and cost basis
    sales_df["Proceeds (CAD)"] = sales_df["Sale Price (CAD)"] * (-sales_df["Shares Added/Sold"])
    sales_df["Cost Basis (CAD)"] = sales_df["ACB Impact (CAD)"].abs()
    
    # Group by year
    annual_summary = sales_df.groupby("Year").agg({
        "Proceeds (CAD)": "sum",
        "Cost Basis (CAD)": "sum",
        "Capital Gain/Loss (CAD)": "sum"
    }).reset_index()
    
    # Save to Annual Summary sheet
    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:
        annual_summary.to_excel(writer, sheet_name="Annual Summary", index=False)
    
    print("Annual summary updated.")