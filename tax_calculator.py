from decimal import Decimal, getcontext

getcontext().prec = 8  # High precision for financial calculations

def calculate_tax_data(data, exchange_rate):
    """Calculate taxable income and ACB for RSU_Vest or ESPP transactions."""
    if data["type"] == "RSU_Vest":
        # RSU Vesting (USD calculations first)
        fmv_usd = Decimal(str(data["fmv_usd"]))
        shares_vested = Decimal(str(data["shares"]))
        
        # Taxable income (USD -> CAD)
        taxable_income_usd = fmv_usd * shares_vested
        taxable_income_cad = taxable_income_usd * Decimal(str(exchange_rate))
        
        # ACB in USD
        total_acb_usd = fmv_usd * shares_vested
        
        return {
            "taxable_income_cad": float(taxable_income_cad),
            "capital_gain_loss": 0.0,
            "total_acb_usd": float(total_acb_usd),
            "total_acb_cad": float(total_acb_usd * Decimal(str(exchange_rate)))
        }
    
    elif data["type"] == "ESPP":
        # ESPP Purchase (USD calculations first)
        fmv_usd = Decimal(str(data["fmv_usd"]))
        purchase_price_usd = Decimal(str(data["purchase_price_usd"]))
        shares = Decimal(str(data["shares"]))
        
        # Taxable benefit (USD -> CAD)
        taxable_benefit_usd = (fmv_usd - purchase_price_usd) * shares
        taxable_income_cad = taxable_benefit_usd * Decimal(str(exchange_rate))
        
        # ACB in USD
        total_acb_usd = fmv_usd * shares
        
        return {
            "taxable_income_cad": float(taxable_income_cad),
            "capital_gain_loss": 0.0,
            "total_acb_usd": float(total_acb_usd),
            "total_acb_cad": float(total_acb_usd * Decimal(str(exchange_rate)))
        }

def process_sale(sale_data, current_shares, current_acb_usd, exchange_rate):
    """Calculate capital gains/losses with USD-based ACB."""
    shares_sold = Decimal(str(abs(sale_data["shares_sold"])))
    sale_price_usd = Decimal(str(sale_data["sale_price_usd"]))
    
    if current_shares <= 0:
        raise ValueError("No shares to sell!")
    
    # ACB per share (USD)
    acb_per_share_usd = Decimal(str(current_acb_usd)) / Decimal(str(current_shares))
    
    # Proceeds (USD -> CAD)
    proceeds_usd = shares_sold * sale_price_usd
    proceeds_cad = proceeds_usd * Decimal(str(exchange_rate))
    
    # ACB of sold shares (USD -> CAD)
    acb_sold_usd = shares_sold * acb_per_share_usd
    acb_sold_cad = acb_sold_usd * Decimal(str(exchange_rate))
    
    # Capital gain/loss (CAD)
    capital_gain_loss = proceeds_cad - acb_sold_cad
    
    return {
        "proceeds_cad": float(proceeds_cad),
        "acb_sold_usd": float(acb_sold_usd),
        "acb_sold_cad": float(acb_sold_cad),
        "capital_gain_loss": float(capital_gain_loss),
        "acb_per_share_usd": float(acb_per_share_usd)
    }