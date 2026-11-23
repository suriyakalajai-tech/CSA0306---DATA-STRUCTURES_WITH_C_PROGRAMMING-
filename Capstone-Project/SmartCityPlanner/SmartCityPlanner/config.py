import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-secret-before-deployment")
    DATABASE = BASE_DIR / "instance" / "smartcity.db"
    REPORT_DIR = BASE_DIR / "reports"
