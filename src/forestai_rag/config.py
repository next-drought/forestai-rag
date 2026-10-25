import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
SETTINGS = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text())
DATABASE_URL = os.environ.get("DATABASE_URL", "")
# Env overrides so model names can change without rebuilding the image.
SETTINGS["models"]["generation"] = os.environ.get("GEN_MODEL", SETTINGS["models"]["generation"])
SETTINGS["models"]["embedding"] = os.environ.get("EMBED_MODEL", SETTINGS["models"]["embedding"])
