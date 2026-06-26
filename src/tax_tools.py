import pandas as pd
from pypdf import PdfReader
import os

def analyze_financial_statement(file_path: str) -> str:
    """Membaca dan merangkum isi laporan keuangan (PDF atau Excel).
    Args:
        file_path: Path ke file laporan keuangan.
    """
    try:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.pdf':
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages[:10]: # Batasi 10 halaman awal
                text += page.extract_text()
            return f"Isi Laporan Keuangan (PDF):\n{text[:2000]}..." # Berikan potongan teks untuk dianalisis LLM
        elif ext in ['.xlsx', '.xls', '.csv']:
            df = pd.read_excel(file_path) if ext != '.csv' else pd.read_csv(file_path)
            summary = df.describe().to_string()
            head = df.head().to_string()
            return f"Ringkasan Data Keuangan:\n{summary}\n\n5 Baris Pertama:\n{head}"
        else:
            return "Format file tidak didukung. Gunakan PDF, Excel, atau CSV."
    except Exception as e:
        return f"Gagal menganalisis file: {e}"

def calculate_tax_estimate(turnover: float, tax_rate: float = 0.005) -> str:
    """Menghitung estimasi pajak (default PPh Final 0.5% untuk UMKM).
    Args:
        turnover: Total omset/pendapatan.
        tax_rate: Tarif pajak dalam desimal.
    """
    tax = turnover * tax_rate
    return f"Estimasi Pajak Terutang: Rp {tax:,.2f} (Tarif: {tax_rate*100}%)"

tax_tools = [analyze_financial_statement, calculate_tax_estimate]
