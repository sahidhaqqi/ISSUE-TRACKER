from datetime import datetime
from .deepseek_client import DeepSeekSummaryClient

class SummaryLogic:
    def __init__(self):
        self.client = DeepSeekSummaryClient()
    
    def generate(self, data):
        """Generate summary dari data"""
        
        if not data:
            return "Tidak ada data untuk digenerate."
        
        # Format data untuk dikirim ke AI
        data_text = "Lokasi\tIssue\tProgress\tTanggal\n"
        for row in data:
            lokasi = row[0]
            issue = row[1][:100]  # potong issue panjang
            progress = row[3]
            tanggal = row[6][:10]  # ambil tanggal aja
            data_text += f"{lokasi}\t{issue}\t{progress}\t{tanggal}\n"
        
        # Generate dengan AI
        result = self.client.generate_summary(data_text)
        
        return result
    
    def generate_simple(self, data):
        """Fallback: generate manual tanpa AI (kalau AI error)"""
        lines = []
        
        # Kelompokkan berdasarkan tanggal
        by_date = {}
        for row in data:
            tgl = row[6][:10]
            if tgl not in by_date:
                by_date[tgl] = []
            by_date[tgl].append(row)
        
        for tgl, items in by_date.items():
            # Format tanggal
            date_obj = datetime.strptime(tgl, "%Y-%m-%d")
            tgl_str = date_obj.strftime("%d %B %Y")
            
            lines.append(f"Laporan Harian – {tgl_str}\n")
            
            for i, row in enumerate(items, 1):
                lokasi = row[0]
                issue = row[1]
                
                # Tentukan awalan
                if "gate" in issue.lower() or "transaksi" in issue.lower():
                    awalan = "Cek issue"
                elif "selisih" in issue.lower():
                    awalan = "Cek issue"
                else:
                    awalan = "Monitoring"
                
                lines.append(f"{i}.{awalan} {issue} di {lokasi}.")
            
            lines.append("")  # baris kosong antar tanggal
        
        return "\n".join(lines)
