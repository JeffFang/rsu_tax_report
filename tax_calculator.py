from decimal import Decimal, getcontext

getcontext().prec = 8  # High precision for financial calculations

def calculate_tax_data(data, exchange_rate):
    """Calculate taxable income and ACB for RSU_Vest or ESPP transactions."""
    if data["type"] == "RSU_Vest":
        # RSU Vesting (shares added, taxable income = FMV × shares_vested)
        fmv_usd = Decimal(str(data["fmv_usd"]))
        shares_vested = Decimal(str(data["shares"]))
        
        # Taxable income (CAD)
        taxable_income_cad = (fmv_usd * shares_vested) * Decimal(str(exchange_rate))
        
        # ACB for kept shares (vested shares - sold shares handled in sale transaction)
        total_acb = fmv_usd * shares_vested * Decimal(str(exchange_rate))
        
        return {
            "taxable_income_cad": float(taxable_income_cad),
            "capital_gain_loss": 0.0,  # Sale-to-cover handled separately
            "total_acb": float(total_acb)
        }
    
    elif data["type"] == "ESPP":
        # ESPP Purchase (taxable benefit = (FMV - purchase price) × shares)
        fmv_usd = Decimal(str(data["fmv_usd"]))
        purchase_price_usd = Decimal(str(data["purchase_price_usd"]))
        shares = Decimal(str(data["shares"]))
        
        # Taxable benefit (USD)
        taxable_benefit_usd = (fmv_usd - purchase_price_usd) * shares
        taxable_income_cad = taxable_benefit_usd * Decimal(str(exchange_rate))
        
        # ACB = FMV × shares (CAD)
        total_acb = fmv_usd * shares * Decimal(str(exchange_rate))
        
        return {
            "taxable_income_cad": float(taxable_income_cad),
            "capital_gain_loss": 0.0,
            "total_acb": float(total_acb)
        }

def process_sale(sale_data, current_shares, current_acb_cad, exchange_rate):
    """Calculate capital gains/losses for a sale transaction."""
    shares_sold = Decimal(str(sale_data["shares_sold"]))
    sale_price_usd = Decimal(str(sale_data["sale_price_usd"]))
    
    if current_shares <= 0:
        raise ValueError("No shares to sell!")
    
    # ACB per share (CAD)
    acb_per_share_cad = Decimal(str(current_acb_cad)) / Decimal(str(current_shares))
    
    # Proceeds (CAD)
    proceeds_cad = shares_sold * sale_price_usd * Decimal(str(exchange_rate))
    
    # ACB of sold shares (CAD)
    acb_sold_cad = shares_sold * acb_per_share_cad
    
    # Capital gain/loss (CAD)
    capital_gain_loss = proceeds_cad - acb_sold_cad
    
    return {
        "proceeds_cad": float(proceeds_cad),
        "acb_sold_cad": float(acb_sold_cad),
        "capital_gain_loss": float(capital_gain_loss),
        "taxable_gain": float(capital_gain_loss * Decimal('0.5'))  # 50% inclusion
    }