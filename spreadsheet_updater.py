import os
import pandas as pd
from openpyxl import load_workbook

# Updated column list with new USD fields
COLUMNS = [
    "Date", "Type", "Shares Added/Sold", "FMV (USD)", "FMV (CAD)",
    "Purchase Price (USD)", "Purchase Price (CAD)", "Sale Price (USD)",
    "Sale Price (CAD)", "Exchange Rate", "Taxable Income (CAD)",
    "ACB Impact (USD)", "ACB Impact (CAD)", "ACB Remaining (USD)",
    "ACB Remaining (CAD)", "ACB per share (USD)", "Capital Gain/Loss (CAD)", 
    "Shares Remaining"
]

def update_spreadsheet(data, tax_data, exchange_rate, shares_remaining, 
                      acb_remaining_usd, acb_remaining_cad, output_path="stock_tracker.xlsx"):
    """Update Transactions sheet with USD-based ACB tracking."""
    try:
        df = pd.read_excel(output_path, sheet_name="Transactions", engine="openpyxl")
    except (FileNotFoundError, ValueError):
        df = pd.DataFrame(columns=COLUMNS)

    # New row template
    new_row = {
        "Date": data["date"],
        "Type": data["type"],
        "Exchange Rate": exchange_rate,
        "Shares Remaining": shares_remaining,
        "ACB Remaining (USD)": acb_remaining_usd,
        "ACB Remaining (CAD)": acb_remaining_cad,
        "ACB per share (USD)": (acb_remaining_usd / shares_remaining) if shares_remaining else 0,
        "Capital Gain/Loss (CAD)": tax_data.get("capital_gain_loss", 0.0)
    }

    # Transaction type handling
    if data["type"] == "RSU_Vest":
        new_row.update({
            "Shares Added/Sold": data["shares"],
            "FMV (USD)": data["fmv_usd"],
            "FMV (CAD)": data["fmv_usd"] * exchange_rate,
            "Taxable Income (CAD)": tax_data["taxable_income_cad"],
            "ACB Impact (USD)": tax_data["total_acb_usd"],
            "ACB Impact (CAD)": tax_data["total_acb_cad"]
        })
    elif data["type"] == "ESPP":
        new_row.update({
            "Shares Added/Sold": data["shares"],
            "FMV (USD)": data["fmv_usd"],
            "FMV (CAD)": data["fmv_usd"] * exchange_rate,
            "Purchase Price (USD)": data["purchase_price_usd"],
            "Purchase Price (CAD)": data["purchase_price_usd"] * exchange_rate,
            "Taxable Income (CAD)": tax_data["taxable_income_cad"],
            "ACB Impact (USD)": tax_data["total_acb_usd"],
            "ACB Impact (CAD)": tax_data["total_acb_cad"]
        })
    elif data["type"] in ["Sale", "Sale_to_Cover"]:
        new_row.update({
            "Shares Added/Sold": -data["shares_sold"],
            "Sale Price (USD)": data["sale_price_usd"],
            "Sale Price (CAD)": data["sale_price_usd"] * exchange_rate,
            "ACB Impact (USD)": -tax_data["acb_sold_usd"],
            "ACB Impact (CAD)": -tax_data["acb_sold_cad"]
        })

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save with proper Excel formatting
    mode = "a" if os.path.exists(output_path) else "w"
    with pd.ExcelWriter(output_path, engine="openpyxl", mode=mode,
                       if_sheet_exists="replace" if mode == "a" else None) as writer:
        df.to_excel(writer, sheet_name="Transactions", index=False)

# (create_annual_summary remains unchanged but will automatically include new columns)
def create_annual_summary(output_path="stock_tracker.xlsx"):
    """Generate Annual Summary with robust file existence checks."""
    if not os.path.exists(output_path):
        print("No transactions file found. Creating empty template.")
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            pd.DataFrame(columns=COLUMNS).to_excel(writer, sheet_name="Transactions", index=False)
            pd.DataFrame(columns=["Year", "Proceeds (CAD)", "Cost Basis (CAD)", "Capital Gain/Loss (CAD)"]).to_excel(writer, sheet_name="Annual Summary", index=False)
        return

    try:
        # Read transactions data
        df = pd.read_excel(output_path, sheet_name="Transactions", engine="openpyxl")
        
        # Create annual summary
        sales_df = df[df["Type"].isin(["Sale", "Sale_to_Cover"])].copy()
        sales_df["Year"] = pd.to_datetime(sales_df["Date"]).dt.year
        annual_summary = sales_df.groupby("Year").agg(
            Proceeds_CAD=("Sale Price (CAD)", lambda x: (x * abs(sales_df.loc[x.index, "Shares Added/Sold"])).sum()),
            Cost_Basis_CAD=("ACB Impact (CAD)", lambda x: abs(x).sum()),
            Capital_Gain_Loss_CAD=("Capital Gain/Loss (CAD)", "sum")
        ).reset_index()

        # Save annual summary
        with pd.ExcelWriter(
            output_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
            annual_summary.to_excel(writer, sheet_name="Annual Summary", index=False)

    except Exception as e:
        print(f"Error generating annual summary: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise