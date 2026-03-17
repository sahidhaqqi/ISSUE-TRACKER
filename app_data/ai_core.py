import json
import re
import numpy as np
from openai import OpenAI
from llama_cpp import Llama
from doctr.models import ocr_predictor
from config import MODEL_PATH, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROMPT_SYSTEM

class AIProcessor:
    def __init__(self):
        self.llm = None
        self.ocr_model = None
        self.deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    def _load_ocr(self):
        """Muat model OCR jika belum dimuat (lazy loading)."""
        if self.ocr_model is None:
            self.ocr_model = ocr_predictor(pretrained=True)

    def _load_llm(self):
        """Muat model LLM offline jika belum dimuat (lazy loading)."""
        if self.llm is None:
            self.llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=8, verbose=False)

    def parse_json_output(self, output_llm, fallback):
        try:
            fixed = output_llm.strip()
            if fixed.startswith('{') and not fixed.endswith('}'):
                last_comma = fixed.rfind(',"issue"')
                fixed = fixed[:last_comma] + '}' if last_comma != -1 else fixed + '"}'
            json_match = re.search(r'\{[^}]*\}', fixed)
            if json_match:
                data = json.loads(json_match.group(0))
                lokasi = data.get("lokasi", "")
                issue = data.get("issue", fallback)
                if len(issue) > 100:
                    issue = issue[:100].rsplit(' ', 1)[0] + "."
                return lokasi, issue
        except Exception:
            pass
        return "", fallback

    def run_pipeline(self, gambar_obj, mode_llm):
        # 1. Pastikan OCR dimuat (lazy loading)
        self._load_ocr()

        # 2. OCR process
        img_array = np.array(gambar_obj.convert('RGB'))
        result = self.ocr_model([img_array])
        raw_text_lines = [
            " ".join([w.value for w in line.words])
            for page in result.pages
            for block in page.blocks
            for line in block.lines
        ]
        raw_text = "\n".join(raw_text_lines).strip()

        if not raw_text:
            return None, "Tidak ada teks."

        # 3. Ekstrak Link
        link_ditemukan = ""
        match_link = re.search(r'(https?://parkee-ticket\.nusa\.technology/front/ticket\.form\.php\?id=\d+)', raw_text)
        if match_link:
            link_ditemukan = match_link.group(1)

        raw_text_trimmed = raw_text[:800]
        fallback_issue = raw_text[:50] + "..."

        # 4. LLM processing
        if mode_llm == "Online (DeepSeek)":
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": f"Extract:\n{raw_text_trimmed}"}
                ],
                max_tokens=120,
                temperature=0.1
            )
            output_llm = response.choices[0].message.content.strip()
        else:
            # Mode offline: pastikan model LLM dimuat (lazy loading)
            self._load_llm()
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": f"Extract:\n{raw_text_trimmed}"}
                ],
                max_tokens=120,
                temperature=0.1
            )
            output_llm = response['choices'][0]['message']['content'].strip()

        lokasi, issue = self.parse_json_output(output_llm, fallback_issue)
        if not lokasi:
            match_lokasi = re.search(r'[Ll]okasi\s*:\s*(.+)', raw_text)
            if match_lokasi:
                lokasi = match_lokasi.group(1).strip()[:50]

        return {"lokasi": lokasi, "issue": issue, "link": link_ditemukan}
