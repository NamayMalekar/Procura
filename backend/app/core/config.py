"""Environment settings (secrets, paths, which brain). Loaded once from .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]          # the backend/ folder
load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self):
        self.app_name = "Procura - AI Purchasing Agent"
        self.database_path = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "procura.db"))
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
        self.agent_brain = os.getenv("AGENT_BRAIN", "auto")          # rules | llm | auto
        self.llm_max_turns = 14
        self.frontend_dist = Path(os.getenv("FRONTEND_DIST", BASE_DIR.parent / "frontend" / "dist"))


settings = Settings()
