import os 
from pathlib import Path 
from dotenv import load_dotenv 
  
# Load .env from project root 
load_dotenv(Path(__file__).parent.parent / '.env') 
  
SCRIPT_DIR = Path(__file__).parent.resolve() 
PROJECT_ROOT = SCRIPT_DIR.parent 
  
# ── Keep your original drive detection logic ─────────────────── 
def detect_environment(): 
    potential_drive_root = SCRIPT_DIR.parent.parent 
    if (potential_drive_root / 'ollama').exists(): 
        return potential_drive_root, True 
    if 'mr_house' in str(SCRIPT_DIR).lower(): 
        return SCRIPT_DIR.parent.parent, False 
    return Path('D:/MrHouse'), True 
  
DRIVE_ROOT, IS_PORTABLE = detect_environment() 
  
class Config: 
    # ── Paths ───────────────────────────────────────────────────── 
    PROJECT_ROOT    = PROJECT_ROOT 
    DRIVE_ROOT      = DRIVE_ROOT 
    IS_PORTABLE     = IS_PORTABLE 
    CHROMA_DB_PATH  = os.getenv('CHROMA_DB_PATH', str(PROJECT_ROOT / 
'chromadb')) 
    KNOWLEDGE_PATH  = os.getenv('KNOWLEDGE_PATH', str(PROJECT_ROOT / 
'app/knowledge/documents')) 
  
    # ── API keys (from .env) ────────────────────────────────────── 
    GROQ_API_KEY    = os.getenv('GROQ_API_KEY', '') 
    GOOGLE_API_KEY  = os.getenv('GOOGLE_API_KEY', '') 
    TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '') 
  
    # ── Model names ─────────────────────────────────────────────── 
    GROQ_SMART_MODEL  = os.getenv('GROQ_SMART_MODEL', 'llama-3.3-70b-versatile') 
    GROQ_FAST_MODEL   = os.getenv('GROQ_FAST_MODEL', 'llama-3.1-8b-instant') 
    GEMINI_MODEL      = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash') 
    LOCAL_SMART_MODEL = os.getenv('LOCAL_SMART_MODEL', 'dolphin3.0-mistral-nemo:12b')
    LOCAL_FAST_MODEL  = os.getenv('LOCAL_FAST_MODEL', 'dolphin3.0-llama3.2:8b') 
    EMBED_MODEL       = os.getenv('EMBED_MODEL', 'nomic-embed-text') 
    VISION_MODEL      = os.getenv('VISION_MODEL', 'moondream') 
  
    # ── Local services (kept from original) ────────────────────── 
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434') 
    API_HOST        = os.getenv('API_HOST', '127.0.0.1') 
    API_PORT        = int(os.getenv('API_PORT', 8000)) 
  
    # ── Kept from original portable_config.py ──────────────────── 
    MODEL_NAME      = os.getenv('LOCAL_SMART_MODEL', 'dolphin3.0-mistral-nemo:12b')
    OLLAMA_HOST     = '127.0.0.1' 
    OLLAMA_PORT     = 11434 
  
    def get_drive_letter(self): 
        return str(self.DRIVE_ROOT)[0:2] 
  
    def get_mode(self): 
        return 'PORTABLE' if self.IS_PORTABLE else 'DEVELOPMENT' 
  
config = Config()