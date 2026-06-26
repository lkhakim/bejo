import json

def calculate_financial_ratios(data: dict) -> str:
    """Menghitung rasio keuangan untuk benchmarking.
    Args:
        data: Dictionary berisi {sales, cogs, gross_profit, operating_profit, net_profit, total_assets, total_debt, current_assets, current_liabilities, inventory}
    """
    try:
        sales = data.get('sales', 0)
        cogs = data.get('cogs', 0)
        gp = data.get('gross_profit', sales - cogs)
        op = data.get('operating_profit', 0)
        np = data.get('net_profit', 0)
        assets = data.get('total_assets', 1) # Avoid div by zero
        debt = data.get('total_debt', 0)
        ca = data.get('current_assets', 0)
        cl = data.get('current_liabilities', 1)
        
        gpm = (gp / sales) * 100 if sales else 0
        npm = (np / sales) * 100 if sales else 0
        opm = (op / sales) * 100 if sales else 0
        der = (debt / (assets - debt)) if (assets - debt) else 0
        cr = (ca / cl)
        cttor = sales / assets if assets else 0
        
        ratios = (
            f"--- Benchmarking Rasio Keuangan ---\n"
            f"1. GPM (Gross Profit Margin): {gpm:.2f}%\n"
            f"2. NPM (Net Profit Margin): {npm:.2f}%\n"
            f"3. OPM (Operating Profit Margin): {opm:.2f}%\n"
            f"4. DER (Debt to Equity Ratio): {der:.2f}\n"
            f"5. CR (Current Ratio): {cr:.2f}\n"
            f"6. CTTOR (Corporate Tax Turn Over Ratio): {cttor:.2f}\n"
        )
        return ratios
    except Exception as e:
        return f"Gagal menghitung rasio: {e}"

def perform_equalization(type: str, source_a_val: float, source_b_val: float) -> str:
    """Melakukan ekualisasi antar jenis pajak.
    Args:
        type: Jenis ekualisasi ('PPN_vs_PPh', 'Gaji_vs_PPh21', 'Jasa_vs_Unifikasi')
        source_a_val: Nilai dari sumber A (misal: Objek PPN di SPT Masa)
        source_b_val: Nilai dari sumber B (misal: Peredaran Usaha di SPT Tahunan)
    """
    diff = abs(source_a_val - source_b_val)
    percent_diff = (diff / source_a_val * 100) if source_a_val else 0
    
    result = (
        f"--- Analisis Ekualisasi {type} ---\n"
        f"Sumber A: Rp {source_a_val:,.2f}\n"
        f"Sumber B: Rp {source_b_val:,.2f}\n"
        f"Selisih: Rp {diff:,.2f} ({percent_diff:.2f}%)\n"
    )
    
    if diff > (source_a_val * 0.05): # Threshold 5%
        result += "⚠️ ATENSI: Selisih signifikan! Potensi indikasi ketidakpatuhan atau kesalahan pembebanan."
    else:
        result += "✅ Selisih dalam batas wajar."
        
    return result

audit_tools = [calculate_financial_ratios, perform_equalization]
