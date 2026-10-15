"""Settings and business policy numbers. Change policy here."""
import os
from dotenv import load_dotenv

load_dotenv()

# ---- LLM / brain selection -------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
AGENT_BRAIN = os.getenv("AGENT_BRAIN", "auto")  # rules | llm | auto
LLM_MAX_TURNS = 14

# ---- Purchasing policy -----------------------------------------------------
REVIEW_PERIOD_DAYS = int(os.getenv("REVIEW_PERIOD_DAYS", 7))   # how often we can re-order
APPROVAL_THRESHOLD = float(os.getenv("APPROVAL_THRESHOLD", 10000))  # $ above this needs a human
ACCEPT_TOLERANCE = 0.10          # recommendation within +-10% of real need is accepted as-is
MAX_COVER_FACTOR = 1.25          # never end up with more than 125% of the target stock
MIN_SUPPLIER_RELIABILITY = 0.75  # suppliers below this are not used automatically

# ---- Agent loop limits -----------------------------------------------------
MAX_PROPOSAL_ATTEMPTS = 3   # brain gets this many tries to pass the validator
MAX_CYCLES = 3              # propose -> execute -> verify cycles before escalating
