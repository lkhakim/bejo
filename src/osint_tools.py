import whois
import exifread
import os

def get_whois_info(domain: str) -> str:
    """Mengambil informasi pendaftaran domain (WHOIS).
    Args:
        domain: Nama domain (misal: 'google.com')
    """
    try:
        w = whois.whois(domain)
        return str(w)
    except Exception as e:
        return f"Gagal mengambil WHOIS: {e}"

def analyze_image_metadata(image_path: str) -> str:
    """Menganalisis metadata (EXIF) dari sebuah file gambar untuk kebutuhan forensik.
    Args:
        image_path: Path ke file gambar.
    """
    try:
        filepath = os.path.join(os.getcwd(), image_path)
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f)
            if not tags:
                return "Tidak ditemukan metadata EXIF pada gambar ini."
            
            summary = []
            for tag in tags.keys():
                if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                    summary.append(f"{tag}: {tags[tag]}")
            
            return "\n".join(summary)
    except Exception as e:
        return f"Gagal menganalisis metadata: {e}"

# List tools untuk OSINT dasar
osint_tools = [get_whois_info, analyze_image_metadata]
