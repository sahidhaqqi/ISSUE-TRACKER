import os
import base64

# Set path dinamis di dalam folder app_data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "laporan_harian.db")
MODEL_PATH = os.path.join(BASE_DIR, "SmolLM2-1.7B-Instruct-Q2_K.gguf")

# Obfuscation Lapis 1 untuk API Key
_p1 = b'c2stY2Fj'
_p2 = b'MGNiMzA1ZDEx'
_p3 = b'NDI5Y2E0NjIzYjNi'
_p4 = b'Y2JhOTAwNTA='
DEEPSEEK_API_KEY = base64.b64decode(_p1 + _p2 + _p3 + _p4).decode('utf-8')
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

PROMPT_SYSTEM = """Output ONLY valid JSON: {"lokasi": "X", "issue": "Y"}
Rules:
- lokasi: building/parking name only. NOT codes, IDs, or plate numbers.
- issue: max 1 sentence, the main technical problem only. No URLs, no codes, no names.
- NO extra text outside JSON."""
