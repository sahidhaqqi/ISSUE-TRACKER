import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

class DeepSeekSummaryClient:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_summary(self, data_text):
        """Generate laporan harian dari data"""
        
        prompt = f"""Buatkan laporan harian versi netral (tanpa status, tanpa link, tanpa root cause).

Format:
- Judul: Laporan Harian – [tanggal]
- Isi berupa numbering
- Gunakan kalimat singkat diawali dengan "Cek issue" / "Setting" / "Monitoring"
- Sertakan lokasi di akhir kalimat
- Jika ada nominal atau tanggal, tetap ditulis
- Gunakan bahasa santai operasional (gaya TSE)
- Jangan tambahkan penjelasan lain

Berikut datanya:
{data_text}

Hasilnya:"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Kamu adalah asisten yang membantu membuat laporan harian dengan gaya santai operasional TSE."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"
