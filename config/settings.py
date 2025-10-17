"""
Configuration settings for SEO Crew Agent
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_DIR = PROJECT_ROOT / "config"

# API Configuration
DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
ANTHROPIC_MODEL_FAST = "claude-3-5-haiku-20241022"

# Default settings
DEFAULT_DOMAIN = "io.net"
DEFAULT_LOCATION_CODE = 2840  # United States
DEFAULT_LANGUAGE_CODE = "en"
DEFAULT_SERP_DEPTH = 10

# File paths
INTERNAL_LINKS_CSV = DATA_DIR / "Internal-Links-Oct-10- 2025.csv"
FALLBACK_INTERNAL_LINKS_CSV = DATA_DIR / "io_net_pages.csv"

# Output settings
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Content settings
DEFAULT_CONTENT_LENGTH_MIN = 1500
DEFAULT_CONTENT_LENGTH_MAX = 5000
DEFAULT_CONTENT_LENGTH_TARGET = 3000

# Competition analysis settings
COMPETITION_SCORE_THRESHOLDS = {
    "low": 30,
    "medium": 60,
    "high": 85
}

# Seed keywords for io.net
SEED_KEYWORDS = [
    "decentralized gpu",
    "gpu computing",
    "distributed computing",
    "ai training infrastructure",
    "machine learning compute",
    "cloud gpu",
    "gpu cluster",
    "high performance computing",
    "gpu as a service",
    "ai infrastructure",
    "machine learning infrastructure",
    "gpu rental",
    "distributed gpu",
    "gpu cloud computing",
    "ai compute platform"
]

def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with optional default"""
    return os.getenv(key, default)

def validate_config():
    """Validate that required configuration is present"""
    required_vars = ["ANTHROPIC_API_KEY", "DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"]
    missing = []
    
    for var in required_vars:
        if not get_env_var(var):
            missing.append(var)
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True
