import json
import re
import numpy as np
from datetime import datetime
from openai import OpenAI
from llama_cpp import Llama
from doctr.models import ocr_predictor
from config import MODEL_PATH, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROMPT_SYSTEM

BASE_URL_FORM   = "https://parkee-ticket.nusa.technology/front/ticket.form.php?id="
BASE_URL_PUBLIC = "https://parkee-ticket.nusa.technology/public/ticket/"


class AIProcessor:
    def __init__(self):
        self.llm = None
        self.ocr_model = None
        self.deepseek_client = OpenAI(
            api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL
        )

    # -------------------------------------------------------------------------
    # Model loading (lazy)
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Output parsing
    # -------------------------------------------------------------------------

    def parse_json_output(self, output_llm, fallback):
        """Parse JSON {lokasi, issue} dari output LLM, dengan fallback jika gagal."""
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

    # -------------------------------------------------------------------------
    # Link extraction — regex (cepat, tanpa API call)
    # -------------------------------------------------------------------------

    def _ekstrak_link_regex(self, raw_text):
        """
        Ekstrak link GLPi dari teks OCR menggunakan regex multi-lapis.

        Dua format URL yang didukung:
          A) /front/ticket.form.php?id=XXXXX   <- format lama via GLPI
          B) /public/ticket/XXXXX              <- format baru via link publik

        Kesalahan OCR yang ditangani:
          - 'https'         -> 'nttps'          (h salah baca)
          - '://'           -> './/'            (titik dua jadi titik)
          - 'parkee-ticket' -> 'parkee- ticket' (spasi nyasar)
          - '?id='          -> '? d='           (huruf i hilang + spasi)
          - 'Ticket #XXXXX' -> teks biasa tanpa URL

        Kembalikan string URL, atau "" jika tidak ditemukan.
        """
        clean = re.sub(r'\s+', ' ', raw_text)

        # Strategi 1a: Format B dengan domain fuzzy
        m = re.search(
            r'[hn]ttps?[.:/]{1,3}//'
            r'[^\s]*parkee\s*-?\s*ticket[^\s]*'
            r'/public/ticket/(\d{4,6})',
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL_PUBLIC + m.group(1)

        # Strategi 1b: Hanya path format B (domain terpotong)
        m = re.search(r'/public/ticket/(\d{4,6})', clean, re.IGNORECASE)
        if m:
            return BASE_URL_PUBLIC + m.group(1)

        # Strategi 2a: Format A dengan domain fuzzy
        m = re.search(
            r'[hn]ttps?[.:/]{1,3}//'
            r'[^\s]*parkee\s*-?\s*ticket[^\s]*'
            r'/front/ticket[^\s]*'
            r'[?&]\s*i?\s*d\s*=\s*(\d{4,6})',
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL_FORM + m.group(1)

        # Strategi 2b: Hanya path ticket.form.php (domain terpotong)
        m = re.search(
            r'ticket\s*[.,]?\s*form\s*[.,]?\s*php'
            r'[^\s]{0,10}'
            r'i?\s*d\s*=\s*(\d{4,6})',
            clean, re.IGNORECASE
        )
        if m:
            return BASE_URL_FORM + m.group(1)

        # Strategi 3: Teks "Ticket #XXXXX" tanpa URL
        m = re.search(r'[Tt]icket\s*#\s*(\d{4,6})', clean)
        if m:
            return BASE_URL_PUBLIC + m.group(1)

        # Strategi 4: Konteks baris GLPI
        m = re.search(r'GLPI\s*[:\-]?\s*(.{5,150})', clean, re.IGNORECASE)
        if m:
            ctx = m.group(1)
            id_m = re.search(r'/public/ticket/(\d{4,6})', ctx, re.IGNORECASE)
            if id_m:
                return BASE_URL_PUBLIC + id_m.group(1)
            id_m = re.search(r'i?\s*d\s*=\s*(\d{4,6})', ctx, re.IGNORECASE)
            if id_m:
                return BASE_URL_FORM + id_m.group(1)

        # Strategi 5: Fallback global
        m = re.search(r'/ticket/(\d{4,6})', clean, re.IGNORECASE)
        if m:
            return BASE_URL_PUBLIC + m.group(1)

        m = re.search(r'(?<![a-zA-Z])i?\s*d\s*=\s*(\d{4,6})', clean, re.IGNORECASE)
        if m:
            return BASE_URL_FORM + m.group(1)

        return ""

    # -------------------------------------------------------------------------
    # Link extraction — AI fallback (dipanggil hanya jika regex gagal)
    # -------------------------------------------------------------------------

    def _ekstrak_link_via_ai(self, raw_text, mode_llm):
        """
        Minta LLM mencari nomor tiket dari teks OCR yang berantakan.
        Dipanggil hanya sebagai fallback saat regex gagal total.

        LLM diminta balas HANYA angka (4-6 digit) atau 'TIDAK ADA'.
        Hasil divalidasi sebelum dipakai agar tidak menerima halusinasi.
        """
        prompt = (
            "Dari teks berikut yang berasal dari OCR (mungkin berantakan), "
            "temukan nomor tiket parkee. Nomor tiket adalah angka 4 sampai 6 digit "
            "yang biasanya muncul setelah kata 'Ticket #', 'id=', '/ticket/', atau 'GLPI'.\n\n"
            "Balas HANYA dengan angkanya saja, tanpa teks, tanpa spasi, tanpa tanda baca. "
            "Jika tidak ada nomor tiket, balas persis: TIDAK ADA\n\n"
            f"Teks:\n{raw_text[:600]}"
        )
        try:
            if mode_llm == "Online (DeepSeek)":
                resp = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0.0,
                )
                hasil = resp.choices[0].message.content.strip()
            else:
                self._load_llm()
                resp = self.llm.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0.0,
                )
                hasil = resp["choices"][0]["message"]["content"].strip()

            # Validasi: harus murni angka 4-6 digit, bukan "TIDAK ADA" atau lainnya
            if hasil.isdigit() and 4 <= len(hasil) <= 6:
                return BASE_URL_PUBLIC + hasil

        except Exception:
            pass

        return ""

    # -------------------------------------------------------------------------
    # Debug logging
    # -------------------------------------------------------------------------

    def _log_ocr_debug(self, raw_text, sumber="link tidak ditemukan"):
        """Simpan teks OCR mentah ke file log untuk debugging."""
        try:
            with open('ocr_debug.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n--- {timestamp} ({sumber}) ---\n{raw_text}\n")
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Main pipeline
    # -------------------------------------------------------------------------

    def run_pipeline(self, gambar_obj, mode_llm, progress_callback=None):
        """
        Jalankan pipeline lengkap: OCR -> Ekstrak link (regex + AI) -> LLM.

        Alur ekstraksi link:
          1. Regex multi-lapis (cepat, tanpa API call)
          2. Jika regex gagal -> AI fallback (LLM yang sama dengan mode aktif)
          3. Jika keduanya gagal -> link kosong, log ke ocr_debug.log

        progress_callback(step, message, percent)
        """

        # Step 1: Muat OCR
        if progress_callback:
            progress_callback(1, "Memuat model OCR...", 10)
        self._load_ocr()

        # Step 2: Baca gambar
        if progress_callback:
            progress_callback(2, "OCR: Membaca gambar...", 30)
        img_array = np.array(gambar_obj.convert('RGB'))
        result = self.ocr_model([img_array])

        # Step 3: Ekstrak teks dari hasil OCR
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

        raw_text_trimmed = raw_text[:800]
        fallback_issue   = raw_text[:50] + "..."

        # Step 4: Ekstrak link — regex dulu, AI jika regex gagal
        if progress_callback:
            progress_callback(4, "Mencari link tiket...", 55)

        link_ditemukan = self._ekstrak_link_regex(raw_text)

        if not link_ditemukan:
            if progress_callback:
                progress_callback(4, "AI: Mencari link tiket...", 60)
            link_ditemukan = self._ekstrak_link_via_ai(raw_text, mode_llm)

        if not link_ditemukan:
            self._log_ocr_debug(raw_text)

        # Step 5: Proses LLM untuk ekstrak lokasi & issue
        if mode_llm == "Online (DeepSeek)":
            if progress_callback:
                progress_callback(5, "Online AI: Menghubungi DeepSeek...", 70)

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
                progress_callback(6, "Online AI: Memproses respons...", 90)

            output_llm = response.choices[0].message.content.strip()

        else:
            if progress_callback:
                progress_callback(5, "Offline AI: Memuat model Llama...", 65)
            self._load_llm()

            if progress_callback:
                progress_callback(6, "Offline AI: Mengekstrak informasi...", 80)

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
            progress_callback(7, "Memproses hasil...", 95)

        # Step 6: Parse JSON output LLM
        lokasi, issue = self.parse_json_output(output_llm, fallback_issue)

        if not lokasi:
            match_lokasi = re.search(r"[Ll]okasi\s*:\s*(.+)", raw_text)
            if match_lokasi:
                lokasi = match_lokasi.group(1).strip()[:50]

        if progress_callback:
            progress_callback(8, "Selesai!", 100)

        return {"lokasi": lokasi, "issue": issue, "link": link_ditemukan}
