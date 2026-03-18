import json
import re
import numpy as np
from datetime import datetime
from openai import OpenAI
from llama_cpp import Llama
from doctr.models import ocr_predictor
from config import MODEL_PATH, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROMPT_SYSTEM

BASE_URL = "https://parkee-ticket.nusa.technology/front/ticket.form.php?id="


class AIProcessor:
    def __init__(self):
        self.llm = None
        self.ocr_model = None
        self.deepseek_client = OpenAI(
            api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL
        )

    def _load_ocr(self):
        """Muat model OCR jika belum dimuat (lazy loading)."""
        if self.ocr_model is None:
            self.ocr_model = ocr_predictor(pretrained=True)

    def _load_llm(self):
        """Muat model LLM offline jika belum dimuat (lazy loading)."""
        if self.llm is None:
            self.llm = Llama(
                model_path=MODEL_PATH, n_ctx=2048, n_threads=8, verbose=False
            )

    def parse_json_output(self, output_llm, fallback):
        try:
            fixed = output_llm.strip()
            if fixed.startswith("{") and not fixed.endswith("}"):
                last_comma = fixed.rfind(',"issue"')
                fixed = fixed[:last_comma] + "}" if last_comma != -1 else fixed + '"}'
            json_match = re.search(r"\{[^}]*\}", fixed)
            if json_match:
                data = json.loads(json_match.group(0))
                lokasi = data.get("lokasi", "")
                issue = data.get("issue", fallback)
                if len(issue) > 100:
                    issue = issue[:100].rsplit(" ", 1)[0] + "."
                return lokasi, issue
        except Exception:
            pass
        return "", fallback

    def _ekstrak_link(self, raw_text):
        """
        Ekstrak link GLPi dari teks OCR dengan toleransi penuh terhadap kesalahan baca.

        Kesalahan OCR yang sudah diketahui dan ditangani:
          - 'https'  →  'nttps'  (h salah baca jadi n)
          - '://'    →  './/'    (titik dua jadi titik)
          - 'parkee-ticket' → 'parkee- ticket'  (spasi nyasar setelah tanda hubung)
          - '?id='   →  '? d='   (huruf i hilang, ada spasi)

        Strategi (dari paling ketat ke paling longgar):
          1. URL persis / URL dengan domain fuzzy
          2. Konteks 'ticket.form.php' + id fuzzy
          3. Konteks baris GLPI + id fuzzy
          4. Fallback global: cari 'i?d=' dengan spasi di mana saja
        """
        # Normalkan semua whitespace jadi spasi tunggal untuk pencarian
        clean = re.sub(r'\s+', ' ', raw_text)

        # --- Strategi 1: URL utuh (toleran terhadap https vs nttps, :// vs .//) ---
        # Menangani: nttps.//parkee- ticket.nusa.technology/.../ticket.form.php? d=30611
        m = re.search(
            r'[hn]ttps?[.:/]{1,3}//'           # protokol fuzzy
            r'[^\s]*parkee\s*-?\s*ticket[^\s]*' # domain parkee[-]ticket fuzzy
            r'/front/ticket'                    # path awal
            r'[^\s]*'                           # sisa path (toleran karakter aneh)
            r'[?&]\s*i?\s*d\s*=\s*(\d{4,6})',  # ?id= atau ? d= atau ?d=
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL + m.group(1)

        # --- Strategi 2: Hanya path ticket.form.php (tanpa domain) ---
        # Menangani jika domain terpotong tapi path terbaca
        m = re.search(
            r'ticket\s*[.,]?\s*form\s*[.,]?\s*php'  # ticket.form.php fuzzy
            r'[^\s]{0,10}'                           # karakter ?/& yang mungkin aneh
            r'i?\s*d\s*=\s*(\d{4,6})',              # id= fuzzy
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL + m.group(1)

        # --- Strategi 3: Cari di baris/konteks yang mengandung kata 'GLPI' ---
        # Menangani: "GLPI: nttps.//...? d=30611"
        m = re.search(r'GLPI\s*[:\-]?\s*(.{5,120})', clean, re.IGNORECASE)
        if m:
            glpi_context = m.group(1)
            id_m = re.search(r'i?\s*d\s*=\s*(\d{4,6})', glpi_context, re.IGNORECASE)
            if id_m:
                return BASE_URL + id_m.group(1)

        # --- Strategi 4: Fallback global — cari pola 'd=' di mana saja ---
        # Cocok untuk: '? d=30611', '?id=30611', 'id=30611', 'd=30611'
        # Dibatasi: angka 4–6 digit agar tidak salah ambil angka lain
        m = re.search(
            r'(?<![a-zA-Z])'       # tidak didahului huruf (hindari false positive)
            r'i?\s*d\s*=\s*(\d{4,6})',
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL + m.group(1)

        return ""

    def _log_ocr_debug(self, raw_text):
        """Simpan teks OCR ke file log untuk keperluan debugging."""
        try:
            with open('ocr_debug.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n--- {timestamp} (link tidak ditemukan) ---\n{raw_text}\n")
        except Exception:
            pass

    def run_pipeline(self, gambar_obj, mode_llm, progress_callback=None):
        """
        Jalankan pipeline OCR + LLM dengan progress callback.
        progress_callback(step, message, percent)
        """

        # 1. Muat model OCR
        if progress_callback:
            progress_callback(1, "Memuat model OCR...", 10)

        self._load_ocr()

        if progress_callback:
            progress_callback(2, "OCR: Membaca gambar...", 30)

        # 2. Proses OCR
        img_array = np.array(gambar_obj.convert('RGB'))
        result = self.ocr_model([img_array])

        if progress_callback:
            progress_callback(3, "OCR: Mengekstrak teks...", 50)

        raw_text_lines = [
            " ".join([w.value for w in line.words])
            for page in result.pages
            for block in page.blocks
            for line in block.lines
        ]
        raw_text = "\n".join(raw_text_lines).strip()

        if not raw_text:
            return None, "Tidak ada teks."

        # 3. Ekstrak Link GLPi (dengan toleransi kesalahan OCR)
        link_ditemukan = self._ekstrak_link(raw_text)

        if not link_ditemukan:
            self._log_ocr_debug(raw_text)

        raw_text_trimmed = raw_text[:800]
        fallback_issue = raw_text[:50] + "..."

        # 4. Proses LLM
        if mode_llm == "Online (DeepSeek)":
            if progress_callback:
                progress_callback(4, "Online AI: Menghubungi DeepSeek...", 70)

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": f"Extract this text and respond in Indonesian:\n{raw_text_trimmed}"},
                ],
                max_tokens=120,
                temperature=0.1,
            )

            if progress_callback:
                progress_callback(5, "Online AI: Memproses respons...", 90)

            output_llm = response.choices[0].message.content.strip()

        else:
            # Mode offline: pastikan model LLM dimuat (lazy loading)
            if progress_callback:
                progress_callback(4, "Offline AI: Memuat model Llama...", 60)

            self._load_llm()

            if progress_callback:
                progress_callback(5, "Offline AI: Mengekstrak informasi...", 80)

            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": f"Extract:\n{raw_text_trimmed}"},
                ],
                max_tokens=120,
                temperature=0.1,
            )
            output_llm = response["choices"][0]["message"]["content"].strip()

        if progress_callback:
            progress_callback(6, "Memproses hasil...", 95)

        # 5. Parse output LLM
        lokasi, issue = self.parse_json_output(output_llm, fallback_issue)

        if not lokasi:
            match_lokasi = re.search(r"[Ll]okasi\s*:\s*(.+)", raw_text)
            if match_lokasi:
                lokasi = match_lokasi.group(1).strip()[:50]

        if progress_callback:
            progress_callback(7, "Selesai!", 100)

        return {"lokasi": lokasi, "issue": issue, "link": link_ditemukan}
