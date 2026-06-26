import json
import os

PROFILING_DB = "taxpayer_profiles.json"

def save_taxpayer_data(npwp: str, data_type: str, amount: float, description: str = "") -> str:
    """Menyimpan data perpajakan spesifik untuk profiling Wajib Pajak.
    Args:
        npwp: Nomor Pokok Wajib Pajak atau ID unik WP.
        data_type: Jenis data ('SPT', 'Faktur', 'Bupot', 'Setoran').
        amount: Nilai nominal rupiah.
        description: Keterangan tambahan (misal: 'Masa Jan 2024').
    """
    try:
        db = {}
        if os.path.exists(PROFILING_DB):
            with open(PROFILING_DB, 'r') as f:
                db = json.load(f)
        
        if npwp not in db:
            db[npwp] = {"SPT": [], "Faktur": [], "Bupot": [], "Setoran": []}
        
        if data_type not in db[npwp]:
            return f"Jenis data {data_type} tidak valid. Gunakan: SPT, Faktur, Bupot, atau Setoran."
            
        entry = {"amount": amount, "description": description}
        db[npwp][data_type].append(entry)
        
        with open(PROFILING_DB, 'w') as f:
            json.dump(db, f, indent=4)
            
        return f"Data {data_type} sebesar Rp {amount:,.2f} untuk WP {npwp} berhasil disimpan."
    except Exception as e:
        return f"Gagal menyimpan data profiling: {e}"

def analyze_taxpayer_compliance(npwp: str) -> str:
    """Menganalisis profil WP dan menghitung Pajak Terutang vs Kurang Bayar.
    Args:
        npwp: Nomor Pokok Wajib Pajak atau ID unik WP.
    """
    try:
        if not os.path.exists(PROFILING_DB):
            return "Belum ada data profiling yang disimpan."
            
        with open(PROFILING_DB, 'r') as f:
            db = json.load(f)
            
        if npwp not in db:
            return f"Data untuk WP {npwp} tidak ditemukan."
            
        wp_data = db[npwp]
        total_spt = sum(item['amount'] for item in wp_data.get('SPT', []))
        total_faktur = sum(item['amount'] for item in wp_data.get('Faktur', []))
        total_bupot = sum(item['amount'] for item in wp_data.get('Bupot', []))
        total_setoran = sum(item['amount'] for item in wp_data.get('Setoran', []))
        
        # Logika sederhana: Pajak Terutang biasanya berdasarkan Faktur atau SPT
        # Kurang Bayar = (Pajak Terutang) - (Bupot + Setoran)
        pajak_terutang = max(total_spt, total_faktur)
        kredit_pajak = total_bupot + total_setoran
        kurang_bayar = pajak_terutang - kredit_pajak
        
        analysis = (
            f"--- Profiling Kepatuhan WP: {npwp} ---\n"
            f"1. Total SPT Dilaporkan: Rp {total_spt:,.2f}\n"
            f"2. Total Faktur Pajak: Rp {total_faktur:,.2f}\n"
            f"3. Total Bukti Potong: Rp {total_bupot:,.2f}\n"
            f"4. Total Setoran (SSP): Rp {total_setoran:,.2f}\n"
            f"----------------------------------------\n"
            f"ESTIMASI PAJAK TERUTANG: Rp {pajak_terutang:,.2f}\n"
            f"TOTAL KREDIT PAJAK: Rp {kredit_pajak:,.2f}\n"
            f"POTENSI KURANG BAYAR: Rp {max(0, kurang_bayar):,.2f}\n"
        )
        
        if kurang_bayar > 0:
            analysis += "\n⚠️ PERINGATAN: Terdapat indikasi kurang bayar. Segera siapkan SP2DK!"
        else:
            analysis += "\n✅ Status WP sementara terlihat patuh."
            
        return analysis
    except Exception as e:
        return f"Gagal melakukan analisis compliance: {e}"

profiling_tools = [save_taxpayer_data, analyze_taxpayer_compliance]
