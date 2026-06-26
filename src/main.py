import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import tools_list
from face_tools import register_face, identify_person
from osint_tools import osint_tools
from tax_tools import tax_tools
from tax_profiling import profiling_tools
from tax_audit import audit_tools
from voice_tools import speak_text

# Update tools list with all capabilities
tools_list.extend([register_face, identify_person])
tools_list.extend(osint_tools)
tools_list.extend(tax_tools)
tools_list.extend(profiling_tools)
tools_list.extend(audit_tools)

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

genai.configure(api_key=api_key)

# Initialize model with tools and personality
system_instruction = (
    "Kamu adalah Bejo, asisten AI Account Representative (AR) dan Auditor Pajak Senior yang sangat jenius, tajam, dan humoris.\n\n"
    "KEAHLIAN AUDIT TINGKAT LANJUTMU:\n"
    "1. BENCHMARKING: Kamu bisa menghitung dan menganalisis rasio keuangan (GPM, NPM, OPM, DER, CR, CTTOR) untuk membandingkan dengan rata-rata industri.\n"
    "2. EKUALISASI: Kamu ahli dalam melakukan rekonsiliasi antar jenis pajak (Ekualisasi PPN vs PPh, Gaji vs PPh 21, Biaya Jasa vs PPh Unifikasi).\n"
    "3. ANALISIS ARUS KAS: Kamu bisa menguji kewajaran omset melalui pengujian arus kas dan arus piutang.\n"
    "4. PROFILING & COMPLIANCE: Kamu mendeteksi potensi kurang bayar dengan membandingkan SPT, Faktur, Bupot, dan Setoran.\n\n"
    "MISI: Menjadi partner investigasi digital Bos untuk memastikan kepatuhan pajak yang maksimal. "
    "Berikan analisis yang 'ngeri-ngeri sedap' tapi tetap dalam gaya bahasa santai dan lucu (panggil 'Bos').\n\n"
    "Selalu rekomendasikan penerbitan SP2DK jika rasio keuangan atau hasil ekualisasi menunjukkan selisih yang tidak wajar."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=tools_list,
    system_instruction=system_instruction
)

def main():
    print("--- Bejo AI: Siap Melayani, Bos! (Version 1.0) ---")
    print("Bejo: Halo Bos! Ada yang bisa Bejo bantu hari ini? Jangan sungkan ya!")
    print("(Ketik 'keluar' kalau Bos sudah lelah)")
    
    # Enable automatic function calling
    chat = model.start_chat(history=[], enable_automatic_function_calling=True)
    
    while True:
        try:
            user_input = input("Anda: ")
            if user_input.lower() in ['keluar', 'exit', 'quit']:
                print("Bejo: Sampai jumpa lagi!")
                speak_text("Sampai jumpa lagi Bos!")
                break
                
            response = chat.send_message(user_input)
            print(f"Bejo: {response.text}")
            
            # Speak the response
            speak_text(response.text)
            
        except KeyboardInterrupt:
            print("\nBejo: Sampai jumpa lagi!")
            speak_text("Sampai jumpa lagi Bos!")
            break
        except Exception as e:
            print(f"Bejo: Waduh, ada error nih: {e}")

if __name__ == "__main__":
    main()
